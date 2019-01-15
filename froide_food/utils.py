from datetime import timedelta
import logging
import re
from urllib.parse import urlencode, quote

from django.urls import reverse
from django.utils import timezone
from django.contrib.gis.geos import Point

try:
    from django.contrib.gis.geoip2 import GeoIP2
except ImportError:
    GeoIP2 = None

from geopy.distance import distance as geopy_distance

from froide.publicbody.models import PublicBody
from froide.foirequest.models import FoiRequest
from froide.georegion.models import GeoRegion
from froide.helper.utils import get_client_ip

from .models import VenueRequestItem
from .geocode import geocode

TIME_PERIOD = timedelta(days=90)
MAX_REQUEST_COUNT = 3

logger = logging.getLogger(__name__)

CITY_RE = re.compile(r'\d{5} ([\w -]+)')
CITY2_RE = re.compile(r', ([\w -]+)$')

TITLE_RE = re.compile(r'Kontrollbericht (?:für|zu) ([\w -]+)(?:, ([\w -]+))?$')
PLZ_RE = re.compile(r'(\d{5}) ([\w -]+)')

Q1 = '1. Wann haben die beiden letzten lebensmittelrechtlichen Betriebsüberprüfungen im folgenden Betrieb stattgefunden:'
Q2 = '2. Kam es hierbei zu Beanstandungen? Falls ja, beantrage ich hiermit die Herausgabe des entsprechenden Kontrollberichts an mich.'


def get_hygiene_publicbodies(lat, lng):
    point = Point(lng, lat)

    regions = GeoRegion.objects.filter(
        geom__covers=point,
    ).exclude(
        kind__in=['country', 'zipcode']
    ).order_by('kind')
    regions = list(regions)
    if not regions:
        raise ValueError('Dieser Ort scheint nicht in Deutschland zu sein!')

    return PublicBody.objects.filter(
        categories__name='Lebensmittelüberwachung',
        regions__in=regions
    )


def get_hygiene_publicbody(lat, lng):
    pbs = get_hygiene_publicbodies(lat, lng)
    if len(pbs) == 0:
        raise ValueError('Keine Behörde gefunden!')
    elif len(pbs) > 1:
        raise ValueError('Mehr als eine Behörde gefunden')
    return pbs[0]


def is_address_bad(addr):
    return CITY_RE.search(addr) is None


def get_city(place):
    if place.get('city'):
        return place['city']
    match = CITY_RE.search(place['address'])
    if match is not None:
        return match.group(1)
    address = place['address']
    address = address.replace(', Deutschland', '')
    match = CITY2_RE.search(address)
    if match is not None:
        return match.group(1)
    return ''


def make_request_url(place, publicbody):
    pb_slug = publicbody.slug
    url = reverse('foirequest-make_request', kwargs={
        'publicbody_slug': pb_slug
    })
    city = get_city(place)
    if city:
        subject = 'Kontrollbericht zu {name}, {city}'.format(
            name=place['name'],
            city=city
        )
    else:
        subject = 'Kontrollbericht zu {name}'.format(
            name=place['name']
        )
    if len(subject) > 250:
        subject = subject[:250] + '...'
    body = '''{q1}
{name}
{address}

{q2}
'''.format(q1=Q1, q2=Q2, **place)
    ref = ('food:%s' % place['ident']).encode('utf-8')
    query = {
        'subject': subject.encode('utf-8'),
        'body': body.encode('utf-8'),
        'ref': ref,
        'law_type': 'VIG',
        'redirect': '/k/lks'  # short, redirects to /kampagnen/lebensmittelkontrolle/gesendet/
    }
    hide_features = (
        'hide_public', 'hide_full_text', 'hide_similar', 'hide_publicbody',
        'hide_draft', 'hide_editing'
    )
    query.update({f: b'1' for f in hide_features})
    query = urlencode(query, quote_via=quote)
    return '%s?%s' % (url, query)


def get_city_from_request(request):
    if GeoIP2 is None:
        return

    ip = get_client_ip(request)
    if not ip:
        logger.warning('No IP found on request: %s', request)
        return

    try:
        g = GeoIP2()
    except Exception as e:
        logger.exception(e)
        return
    try:
        result = g.city(ip)
    except Exception as e:
        logger.exception(e)
        return
    if result and result.get('latitude'):
        return result


def get_request_count(request, pb):
    if request.user.is_authenticated:
        request_count = FoiRequest.objects.filter(
            public_body=pb,
            user=request.user,
            first_message__gte=timezone.now() - TIME_PERIOD
        ).count()
        return request_count
    return 0


def get_name_and_address(venue):
    vris = VenueRequestItem.objects.filter(venue=venue)
    if not vris:
        return
    foirequest = None
    for vri in vris:
        if vri.foirequest is not None:
            foirequest = vri.foirequest
            break
    if not foirequest:
        return
    title = foirequest.title
    match = TITLE_RE.search(title)
    if not match:
        return
    name = match.group(1)
    descr = foirequest.description
    descr = descr.replace(Q1, '')
    descr = descr.replace(Q2, '').strip()
    descr = descr.replace(name, '').strip()
    parts = descr.splitlines()
    address = '\n'.join(parts[-2:]).strip()
    if not address:
        return {'name': name}
    return {
        'name': name,
        'address': address
    }


def match_venue_with_provider(venue, provider):
    from .venue_providers import venue_providers

    if venue.ident.startswith(provider):
        return True
    if venue.context.get('failed_' + provider):
        return False
    if provider in venue.context:
        current, current_id = venue.ident.split(':', 1)
        venue.context[current] = current_id
        venue.ident = provider + ':' + venue.context[provider]
        venue.save()
        return True
    info = get_name_and_address(venue)
    if not info.get('name'):
        print('No name found.')
        return False
    if not venue.geo:
        if not info.get('address'):
            print('No address found.')
            return False
        address = info['address']
        point, formatted_address = geocode(address)
        if not point:
            print('Geocoding failed.')
            return False
        venue.geo = point
        venue.save()
    venue_provider = venue_providers[provider]
    places = venue_provider.match_place(
        coordinates=[
            venue.geo.coords[1],
            venue.geo.coords[0]
        ], name=info['name']
    )
    if not places:
        print('No match found.')
        return False
    place = places[0]
    place_point = Point(place['lng'], place['lat'])
    distance = geopy_distance(place_point, point)
    if distance.meters > 100:
        print('Matches too far away.')
        return False
    venue.context[provider] = place['ident'].split(':', 1)[1]
    current, current_id = venue.ident.split(':', 1)
    venue.context[current] = current_id
    venue.ident = provider + ':' + venue.context[provider]
    venue.save()
    return True

from datetime import timedelta
import logging
from urllib.parse import urlencode, quote

from django.urls import reverse
from django.utils import timezone

try:
    from django.contrib.gis.geoip2 import GeoIP2
except ImportError:
    GeoIP2 = None

from froide.publicbody.models import PublicBody
from froide.foirequest.models import FoiRequest
from froide.georegion.models import GeoRegion
from froide.helper.utils import get_client_ip

TIME_PERIOD = timedelta(days=90)
MAX_REQUEST_COUNT = 3

logger = logging.getLogger(__name__)


def get_hygiene_publicbodies(lat, lng):
    point = 'POINT(%f %f)' % (lng, lat)

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


def make_request_url(place, publicbody):
    pb_slug = publicbody.slug
    url = reverse('foirequest-make_request', kwargs={
        'publicbody_slug': pb_slug
    })

    subject = 'Kontrollbericht zu {name}, {city}'.format(
        name=place['name'],
        city=place['city']
    )
    if len(subject) > 250:
        subject = subject[:250] + '...'
    body = '''1. Wann haben die beiden letzten lebensmittelrechtlichen Betriebsüberprüfungen im folgenden Betrieb stattgefunden:
{name}
{address}

2. Kam es hierbei zu Beanstandungen? Falls ja, beantrage ich hiermit die Herausgabe des entsprechenden Kontrollberichts an mich.
'''.format(**place)
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

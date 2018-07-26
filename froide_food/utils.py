try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.urls import reverse
from django.conf import settings

try:
    from django.contrib.gis.geoip2 import GeoIP2
    from django.contrib.gis.geoip2.base import GeoIP2Exception
except ImportError:
    GeoIP2 = None

from froide.publicbody.models import PublicBody
from froide.georegion.models import GeoRegion
from froide.helper.utils import get_client_ip


def get_hygiene_publicbody(lat, lng):
    point = 'POINT(%f %f)' % (lng, lat)

    regions = GeoRegion.objects.filter(
        geom__covers=point,
    ).order_by('kind')
    if not regions:
        raise ValueError('Dieser Ort scheint nicht in Deutschland zu sein!')

    pbs = PublicBody.objects.filter(
        categories__name='Lebensmittelüberwachung',
        region__in=regions
    )
    if len(pbs) == 0:
        raise ValueError('Keine Behoerde gefunden in %s' % regions)
    elif len(pbs) > 1:
        raise ValueError('Mehr als eine Behoerde gefunden in %s' % regions)
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
    body = '''Den letzten, aktuellen Kontrollbericht der lebensmittelrechtlichen Betriebsüberprüfung von
{name}
{address}'''.format(**place)
    ref = ('food:%s' % place['ident']).encode('utf-8')
    query = {
        'subject': subject.encode('utf-8'),
        'body': body.encode('utf-8'),
        'ref': ref,
        'law_type': 'VIG'
    }
    hide_features = (
        'hide_public', 'hide_full_text', 'hide_similar', 'hide_publicbody',
        'hide_draft', 'hide_editing'
    )
    query.update({f: b'1' for f in hide_features})
    query = urlencode(query)
    return '%s?%s' % (url, query)


def get_city_from_request(request):
    if GeoIP2 is None:
        return

    try:
        g = GeoIP2()
    except GeoIP2Exception:
        return

    ip = get_client_ip(request)
    try:
        result = g.city(ip)
    except Exception:
        return
    if result and result.get('latitude'):
        return result


def get_social_url(ident):
    return '%s%s?%s' % (
        settings.SITE_URL,
        reverse('food-make_request'),
        urlencode({
            'ident': ident.encode('utf-8'),
            'social': b'1'
        }))


def get_social_text(ident, place):
    return (
        'Ich mache gerade bei einer Aktion zu Lebensmittelhygiene mit. '
        'Könntest du mir helfen und den Kontrollbericht von „%s“ '
        'anfragen?\n\n%s' % (
            place['name'], get_social_url(ident)
        )
    )

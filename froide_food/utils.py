try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from django.urls import reverse

from froide.publicbody.models import PublicBody
from froide.georegion.models import GeoRegion


def get_hygiene_publicbody(lat, lng):
    point = 'POINT(%f %f)' % (lng, lat)

    regions = GeoRegion.objects.filter(
        geom__covers=point,
        kind__in=('district', 'borough')
    ).order_by('kind')
    if not regions:
        return ValueError('Nicht in DE')
    region = regions[0]

    pbs = PublicBody.objects.filter(
        categories__name='Lebensmittelüberwachung',
        region=region
    )
    if len(pbs) == 0:
        raise ValueError('Keine Behoerde gefunden in %s' % region)
    elif len(pbs) > 1:
        raise ValueError('Mehr als eine Behoerde gefunden in %s' % region)
    return pbs[0]


def make_request_url(place, publicbody):
    pb_slug = publicbody.slug
    url = reverse('foirequest-make_request', kwargs={
        'publicbody_slug': pb_slug
    })
    subject = 'Letzter Kontrollbericht für {name}, {city}'.format(
        name=place['name'],
        city=place['city']
    )
    if len(subject) > 250:
        subject = subject[:250] + '...'
    body = '''Letzten Kontrollbericht für folgende Einrichtung:
{name}
{address}
    '''.format(**place)
    ref = ('food:%s' % place['ident']).encode('utf-8')
    query = {
        'subject': subject.encode('utf-8'),
        'body': body.encode('utf-8'),
        'ref': ref
    }
    hide_features = (
        'hide_public', 'hide_full_text', 'hide_similar', 'hide_publicbody',
        'hide_draft'
    )
    query.update({f: b'1' for f in hide_features})
    query = urlencode(query)
    return '%s?%s' % (url, query)

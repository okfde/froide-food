import logging
from django.conf import settings
from django.contrib.gis.geos import Point

import geocoder

logger = logging.getLogger()

API_KEY = settings.FROIDE_FOOD_CONFIG.get('api_key_geocode_here')


def run_geocode(search, country='DE'):
    if not API_KEY:
        return
    app_id, app_code = API_KEY.split('|')
    kwargs = {
        'app_id': app_id,
        'app_code': app_code,
        # 'key': API_KEY,
        # 'language': country.lower(),
        # 'components': 'country:%s' % country,
        'headers': {
            'Accept-Language': 'de-DE'
        }
    }
    try:
        result = geocoder.here(search, **kwargs)
        latlng = None
        address = None
        if result.status != 'OK':
            raise Exception('Over query API limit')
        # Here specific
        if result.raw['LocationType'] != 'address':
            # Only accept exact matches
            return
        if result and result.latlng:
            latlng = result.latlng
            address = result.address
        return latlng, address
    except Exception as e:
        logger.exception(e)
        return None


def geocode(q):
    result = run_geocode(q + ', Deutschland')
    if result is None:
        return None, None
    latlng, address = result
    if latlng is None:
        return None, None
    point = Point(latlng[1], latlng[0], srid=4326)
    return point, address

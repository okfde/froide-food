import logging
import re

from django.conf import settings
from django.contrib.gis.geos import Point

import geocoder

from froide.georegion.models import GeoRegion

logger = logging.getLogger()

API_KEY = settings.FROIDE_FOOD_CONFIG.get("api_key_geocode_here")
MAPBOX_API_KEY = settings.FROIDE_FOOD_CONFIG.get("api_key_geocode_mapbox")
PLZ_RE = re.compile(r"^(\d{5})$")


def get_kwargs():
    if not API_KEY:
        raise ValueError
    app_id, app_code = API_KEY.split("|")
    return {
        "app_id": app_id,
        "app_code": app_code,
        # 'key': API_KEY,
        # 'components': 'country:%s' % country,
        "headers": {"Accept-Language": "de-DE"},
        "key": MAPBOX_API_KEY,
        "language": "de",
    }


def get_reverse_kwargs():
    if not MAPBOX_API_KEY:
        raise ValueError
    return {
        "key": MAPBOX_API_KEY,
        "language": "de",
        "types": "address",
    }


def run_geocode(search, country="DE", address=True):
    kwargs = get_kwargs()
    try:
        result = geocoder.mapbox(search, **kwargs)
        latlng = None
        address = None
        if len(result) == 0:
            return None
        if result.status != "OK":
            raise Exception("Over query API limit")
        # Here specific
        if address and result.raw["LocationType"] != "address":
            # Only accept exact matches
            return
        if result and result.latlng:
            latlng = result.latlng
            address = result.address
        return latlng, address
    except Exception as e:
        logger.exception(e)
        return None


def reverse_geocode(latlng):
    kwargs = get_reverse_kwargs()
    try:
        result = geocoder.mapbox(latlng, method="reverse", **kwargs)
        if len(result) == 0:
            return None
        if result.status != "OK":
            raise Exception("Over query API limit")
        if result and result.address:
            return result
        return None
    except Exception as e:
        logger.exception(e)
        return None


def geocode_plz(plz):
    """
    Get centroid of postcode area
    """
    try:
        region = GeoRegion.objects.get(
            slug=plz,
            kind="zipcode",
        )
        return region.geom.centroid, plz
    except GeoRegion.DoesNotExist:
        return None, None


def geocode(q, **kwargs):
    match = PLZ_RE.match(q.strip())
    if match:
        return geocode_plz(match.group(1))
    result = run_geocode(q + ", Deutschland", **kwargs)
    if result is None:
        return None, None
    latlng, address = result
    if latlng is None:
        return None, None
    point = Point(latlng[1], latlng[0], srid=4326)
    return point, address

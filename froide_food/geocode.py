import logging
import re

from django.conf import settings
from django.contrib.gis.geos import Point
from froide.georegion.models import GeoRegion
from geopy.geocoders import MapBox

logger = logging.getLogger()

MAPBOX_API_KEY = settings.FROIDE_FOOD_CONFIG.get("api_key_geocode_mapbox")
PLZ_RE = re.compile(r"^(\d{5})$")


def get_geocoder():
    return MapBox(api_key=MAPBOX_API_KEY)


def run_geocode(search, country="DE"):
    geocoder = get_geocoder()
    try:
        result = geocoder.geocode(search, country=country, language="de")
        if result is None:
            return None
        return (result.latitude, result.longitude), result.address
    except Exception as e:
        logger.exception(e)
        return None


def reverse_geocode(latlng: tuple[float, float]) -> dict[str, str] | None:
    geocoder = get_geocoder()
    try:
        result = geocoder.reverse(latlng)
        if result is None:
            return None
        return result.raw
    except Exception as e:
        logger.exception(e)
        return None


def geocode_plz(plz: str) -> tuple[Point, str] | tuple[None, None]:
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


def geocode(q: str) -> tuple[Point, str] | tuple[None, None]:
    match = PLZ_RE.match(q.strip())
    if match:
        return geocode_plz(match.group(1))
    result = run_geocode(q + ", Deutschland")
    if result is None:
        return None, None
    latlng, address = result
    if latlng is None:
        return None, None
    point = Point(latlng[1], latlng[0], srid=4326)
    return point, address

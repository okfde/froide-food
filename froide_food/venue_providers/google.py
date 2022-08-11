import json
import logging

from django.conf import settings
from django.core.cache import cache

import requests

from .base import BaseVenueProvider, VenueProviderException

logger = logging.getLogger("froide")

TEXTSEARCH_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
LOOKUP_URL = "https://maps.googleapis.com/maps/api/place/details/json"

API_KEY = settings.FROIDE_FOOD_CONFIG.get("api_key_google")

RELEVANT_TYPES = {
    "bakery",
    "bar",
    "food",
    "cafe",
    "gas_station",
    "restaurant",
    "supermarket",
    "night_club",
}

ICON_TYPES = {
    "bakery",
    "bar",
    "cafe",
    "gas_station",
    "restaurant",
    "supermarket",
    "night_club",
}

FILTERS = [
    {
        "name": "Bäckerei/Konditorei",
        "icon": "fa-pie-chart",
        "active": False,
        "categories": ["bakery"],
    },
    {
        "name": "Restaurant/Gaststätte",
        "icon": "fa-cutlery",
        "active": False,
        "categories": ["restaurant"],
    },
    {"name": "Café", "icon": "fa-coffee", "active": False, "categories": ["cafe"]},
    {"name": "Bar", "icon": "fa-glass", "active": False, "categories": ["bar"]},
    {
        "name": "Diskothek/Club",
        "icon": "fa-diamond",
        "active": False,
        "categories": ["night_club"],
    },
    {
        "name": "Supermarkt/Discounter",
        "icon": "fa-shopping-cart",
        "active": False,
        "categories": ["supermarket"],
    },
    {
        "name": "Tankstelle",
        "icon": "fa-car",
        "active": False,
        "categories": ["gas_station"],
    },
]


GERMANY = (47.266667, 5.9, 55.05, 15.033333)


def make_cache_key(
    params,
    method="search",
    keys=(
        "radius",
        "location",
    ),
):
    return "froide_food:google:%s:%s" % (
        method,
        "_".join(str(params.get(key)).replace(" ", "") for key in keys),
    )


class GoogleVenueProvider(BaseVenueProvider):
    name = "google"
    FILTERS = FILTERS
    FIELDS = (
        "formatted_address,geometry/location,name,permanently_closed,place_id,types"
    )

    def get_places(
        self,
        coordinates=None,
        location=None,
        q=None,
        categories=None,
        radius=None,
        **kwargs
    ):
        params = {
            "key": API_KEY,
            "language": "de",
        }
        if location is not None:
            url = TEXTSEARCH_URL
            params.update(
                {
                    "input": location,
                    "fields": "geometry/location",
                    "inputtype": "textquery",
                    "locationbias": "rectangle:%s,%s|%s,%s" % GERMANY,
                }
            )
            cache_key = make_cache_key(params, method="loc", keys=("input",))
            response = cache.get(cache_key)
            if response is not None:
                candidates = json.loads(response).get("candidates")
            else:
                response = requests.get(url, params=params)
                logger.info("API Request: %s", response.request.url)
                cache.set(cache_key, response.text, None)
                candidates = response.json().get("candidates")

            if not candidates:
                return []
            candidate = candidates[0]
            coordinates = (
                candidate["geometry"]["location"]["lat"],
                candidate["geometry"]["location"]["lng"],
            )
            radius = 5000
        can_cache = True
        url = NEARBY_URL
        params.update(
            {
                "location": "{},{}".format(*coordinates),
                "radius": min(radius, 5000),
                "type": "restaurant",
            }
        )
        if q:
            can_cache = False
            params["keyword"] = q
        else:
            params["keyword"] = ""
        params["fields"] = self.FIELDS
        response = None
        if can_cache:
            cache_key = make_cache_key(params)
            response = cache.get(cache_key)

        if response is not None:
            results = json.loads(response)

        if not can_cache or response is None:
            response = requests.get(url, params=params)
            logger.info("API Request: %s", response.request.url)
            if response.json()["status"] != "OK":
                logger.warn(
                    "API response: %s - %s", response.status_code, response.text
                )
                raise VenueProviderException()
            if can_cache:
                cache.set(cache_key, response.text, None)
            results = response.json()

        if "results" not in results:
            return []
        results = results["results"]

        return [
            self.extract_result(r)
            for r in results
            if set(r["types"]) & RELEVANT_TYPES and not r.get("permanently_closed")
        ]

    def extract_result(self, r):
        category = list(set(r["types"]) & ICON_TYPES)
        if category:
            category = category[0]
        else:
            category = ""
        return {
            "ident": "google:%s" % r["place_id"],
            "lat": r["geometry"]["location"]["lat"],
            "lng": r["geometry"]["location"]["lng"],
            "name": r["name"],
            "address": r.get("formatted_address") or r.get("vicinity", ""),
            "category": category,
        }

    def get_place(self, ident):
        if ident.startswith("google:"):
            ident = ident.replace("google:", "")

        params = {
            "key": API_KEY,
            "language": "de",
            "place_id": ident,
            "fields": self.FIELDS,
        }
        response = requests.get(LOOKUP_URL, params=params)

        if response.status_code != 200:
            logger.warn("API response: %s - %s", response.status_code, response.text)
            raise VenueProviderException()

        logger.info("API Request: %s (%s)", response.request.url, response.status_code)
        result = response.json()
        if not result.get("result"):
            raise VenueProviderException()

        return self.extract_result(result["result"])

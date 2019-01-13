import json

from django.conf import settings
from django.core.cache import cache

import requests
import logging

from .base import BaseVenueProvider, VenueProviderException


logger = logging.getLogger('froide')

SEARCH_URL = 'https://api.foursquare.com/v2/venues/search'
LOOKUP_URL = 'https://api.foursquare.com/v2/venues/{ident}'
API_KEY = settings.FROIDE_FOOD_CONFIG.get('api_key_foursquare') or '|'
CLIENT_ID, CLIENT_SECRET = API_KEY.split('|')


def make_cache_key(params, method='search'):
    keys = ('radius', 'latitude', 'longitude')
    return 'froide_food:foursquare:%s:%s' % (
        method,
        '_'.join(
            str(params.get(key)) for key in keys
        )
    )


CATEGORIES = [
  '4d4b7105d754a06374d81259',  # food
  '4bf58dd8d48988d1f9941735',  # Food & Drink Shop
]

HEADERS = {
    'Accept-Language': 'de'
}


class FoursquareVenueProvider(BaseVenueProvider):
    name = 'foursquare'
    FILTERS = []

    def get_places(self, location=None, coordinates=None,
                   q=None, categories=None, radius=None):
        params = {
            'radius': 10000,
            'limit': 50,
            'intent': 'browse',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'v': '20190101'
        }
        can_cache = False
        if location is not None:
            can_cache = False
            params['near'] = location + ', Deutschland'
        else:
            params.update({
                'll': '{},{}'.format(*coordinates)
            })
        if q:
            can_cache = False
            params['query'] = q
        params['categoryId'] = ','.join(CATEGORIES)
        if radius is not None:
            params['radius'] = radius

        response = None
        if can_cache:
            cache_key = make_cache_key(params)
            response = cache.get(cache_key)

        if response is not None:
            results = json.loads(response)
        if not can_cache or response is None:
            response = requests.get(
                SEARCH_URL,
                params=params,
                headers=HEADERS
            )
            logger.info('API Request: %s (%s)',
                        response.request.url, response.status_code)
            if response.status_code != 200:
                logger.warn('API response: %s - %s',
                            response.status_code, response.text)
                raise VenueProviderException()

            if can_cache:
                cache.set(cache_key, response.text, 60 * 10)
            results = response.json()

        if 'response' not in results:
            return []
        results = results['response'].get('venues', [])

        return [
            self.extract_result(r)
            for r in results
            if self.is_in_germany((
                r['location']['lng'],
                r['location']['lat'],
            ))
        ]

    def extract_result(self, r):
        # cats = r['categories']
        # category = None
        # if cats:
        #     category = [CATEGORY_MAPPING.get(c['alias'], None) for c in cats]
        #     category = [c for c in category if c is not None]
        # if category:
        #     category = category[0]
        # else:
        #     category = None

        return {
            'ident': '%s:%s' % (self.name, r['id']),
            'lat': r['location']['lat'],
            'lng': r['location']['lng'],
            'name': r['name'],
            'url': 'https://foursquare.com/v/{id}?ref={clientid}'.format(
                id=r['id'], clientid=CLIENT_ID
            ),
            'address': '\n'.join(r['location']['formattedAddress'][:-1]),
            'city': r['location'].get('city', ''),
        }

    def get_place(self, ident):
        if ident.startswith('foursquare:'):
            ident = ident.replace('foursquare:', '')
        params = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'v': '20190101'
        }
        response = requests.get(
            LOOKUP_URL.format(ident=ident),
            params=params,
            headers=HEADERS
        )
        if response.status_code != 200:
            logger.warn('API response: %s - %s',
                        response.status_code, response.text)
            raise VenueProviderException()

        logger.info('API Request: %s (%s)',
                    response.request.url, response.status_code)
        result = response.json()
        return self.extract_result(result)

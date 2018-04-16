from django.conf import settings

import requests
import logging

from .base import BaseVenueProvider

logger = logging.getLogger('froide')

SEARCH_URL = 'https://api.yelp.com/v3/businesses/search'
LOOKUP_URL = 'https://api.yelp.com/v3/businesses/{ident}'
API_KEY = settings.FROIDE_FOOD_CONFIG.get('api_key_yelp')

RELEVANT_TYPES = [
    'restaurants',
    'food',
    'servicestations'
]


class YelpVenueProvider(BaseVenueProvider):
    def get_places(self, latlng, q=None, categories=None, radius=None):
        params = {
            'latitude': latlng[0],
            'longitude': latlng[1],
            'radius': 10000,
            'limit': 50,
            'locale': 'de_DE'
        }
        if q is not None:
            params['term'] = q
        if categories is not None:
            params['categories'] = ','.join(categories)
        if radius is not None:
            params['radius'] = radius

        response = requests.get(
            SEARCH_URL,
            params=params,
            headers={
                'Authorization': 'Bearer %s' % API_KEY
            }
        )
        logger.info('API Request: %s', response.request.url)
        results = response.json()
        if 'businesses' not in results:
            return []
        results = results['businesses']

        return [
            self.extract_result(r)
            for r in results
        ]

    def extract_result(self, r):
        return {
            'ident': 'yelp:%s' % r['id'],
            'lat': r['coordinates']['latitude'],
            'lng': r['coordinates']['longitude'],
            'name': r['name'],
            'address': '%s, %s %s' % (
                r['location']['address1'],
                r['location']['zip_code'],
                r['location']['city']
            ),
            'city': r['location']['city'],
            'image': r['image_url'],
            'rating': r.get('rating')
        }

    def get_place(self, ident):
        response = requests.get(
            LOOKUP_URL.format(ident=ident),
            params={'locale': 'de_DE'},
            headers={
                'Authorization': 'Bearer %s' % API_KEY
            }
        )
        logger.info('API Request: %s', response.request.url)
        result = response.json()
        return self.extract_result(result)

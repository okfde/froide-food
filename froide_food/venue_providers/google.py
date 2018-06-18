from django.conf import settings

import requests
import logging

from .base import BaseVenueProvider

logger = logging.getLogger('froide')

NEARBY_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

API_KEY = settings.FROIDE_FOOD_CONFIG.get('api_key_google')

RELEVANT_TYPES = [
    'bakery',
    'bar',
    'cafe',
    'gas_station',
    'restaurant',
    'supermarket',
]


class GoogleVenueProvider(BaseVenueProvider):
    name = 'google'

    def get_places(self, latlng, q=None, categories=None, **kwargs):
        params = {
            'key': API_KEY,
            'location': '%s,%s' % latlng,
            'radius': 10000
        }
        if q is not None:
            params['name'] = q
        if categories:
            params['type'] = categories[0]
        response = requests.get(NEARBY_URL, params=params)
        logger.info('API Request: %s', response.request.url)
        results = response.json()
        if 'results' not in results:
            return []
        results = results['results']

        return [
            {
                'ident': 'google:%s' % r['place_id'],
                'lat': r['geometry']['location']['lat'],
                'lng': r['geometry']['location']['lng'],
                'name': r['name'],
                'address': r['vicinity'],
                'image': None,
                'rating': r.get('rating')
            }
            for r in results
        ]

from django.conf import settings

import requests
import logging

from .base import BaseVenueProvider

logger = logging.getLogger('froide')

TEXTSEARCH = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
NEARBY_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

API_KEY = settings.FROIDE_FOOD_CONFIG.get('api_key_google')

RELEVANT_TYPES = {
    'bakery',
    'bar',
    'food',
    'cafe',
    'gas_station',
    'restaurant',
    'supermarket',
    'night_club',
}

GERMANY = (
  47.266667, 5.9,
  55.05, 15.033333
)


class GoogleVenueProvider(BaseVenueProvider):
    name = 'google'
    FILTERS = []
    FIELDS = 'formatted_address,geometry/location,name,permanently_closed,place_id'

    def get_places(self, coordinates=None, location=None, q=None,
                   categories=None, radius=None, **kwargs):
        params = {
            'key': API_KEY,
            'language': 'de',
        }
        if location is not None:
            url = TEXTSEARCH
            params.update({
                'input': location,
                'fields': 'geometry/location',
                'inputtype': 'textquery',
                'locationbias': 'rectangle:%s,%s|%s,%s' % GERMANY
            })
            response = requests.get(url, params=params)
            logger.info('API Request: %s', response.request.url)
            candidates = response.json().get('candidates')
            print(candidates)
            if not candidates:
                return []
            candidate = candidates[0]
            coordinates = (
                candidate['geometry']['location']['lat'],
                candidate['geometry']['location']['lng']
            )
            radius = 5000

        url = NEARBY_URL
        params.update({
            'location': '%s,%s' % coordinates,
            'radius': radius
        })
        if q is not None:
            params['keyword'] = q
        params['fields'] = self.FIELDS
        response = requests.get(url, params=params)
        logger.info('API Request: %s', response.request.url)
        results = response.json()
        print(results)
        if 'results' not in results:
            return []
        results = results['results']

        return [
            {
                'ident': 'google:%s' % r['place_id'],
                'lat': r['geometry']['location']['lat'],
                'lng': r['geometry']['location']['lng'],
                'name': r['name'],
                'address': r.get('formatted_address') or r.get('vicinity', ''),
                'image': None,
                'rating': None,
            }
            for r in results
            if set(r['types']) & RELEVANT_TYPES
            and not r.get('permanently_closed')
        ]

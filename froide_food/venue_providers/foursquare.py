import json
import os

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

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'foursquare.json')


FILTERS = [{
    'name': 'Fleischerei/Metzgerei',
    'icon': 'fa-paw',
    'active': False,
    'categories': ['4bf58dd8d48988d11d951735']
    },
    {
    'name': 'Bäckerei/Konditorei',
    'icon': 'fa-pie-chart',
    'active': False,
    'categories': ['4bf58dd8d48988d16a941735']
    },
    {
    'name': 'Restaurant/Gaststätte',
    'icon': 'fa-cutlery',
    'active': False,
    'categories': ['4d4b7105d754a06374d81259']
    },
    {
    'name': 'Café/Bar',
    'icon': 'fa-coffee',
    'active': False,
    'categories': ['4bf58dd8d48988d16d941735']
    },
    {
    'name': 'Eisdiele',
    'icon': 'fa-child',
    'active': False,
    'categories': ['4bf58dd8d48988d1d0941735']
    },
    {
    'name': 'Kiosk/Spätkauf',
    'icon': 'fa-beer',
    'active': False,
    'categories': ['4bf58dd8d48988d146941735']
    },
    {
    'name': 'Diskothek/Club',
    'icon': 'fa-diamond',
    'active': False,
    'categories': ['4d4b7105d754a06376d81259']
    },
    # {
    # 'name': 'Imbiss',
    # 'icon': 'fa-soccer-ball-o',
    # 'active': False,
    # 'categories': ['foodtrucks', 'foodstands']
    # },
    {
    'name': 'Systemgastronomie',
    'icon': 'fa-bars',
    'active': False,
    'categories': ['4bf58dd8d48988d16e941735']
    },
    {
    'name': 'Hotel/Pension',
    'icon': 'fa-bed',
    'active': False,
    'categories': ['4bf58dd8d48988d1fa931735']
    },
    {
    'name': 'Supermarkt/Discounter',
    'icon': 'fa-shopping-cart',
    'active': False,
    'categories': ['52f2ab2ebcbc57f1066b8b46']
    },
    {
    'name': 'Einzelhandel',
    'icon': 'fa-shopping-basket',
    'active': False,
    'categories': ['4bf58dd8d48988d1f9941735']
    },
    {
    'name': 'Tankstelle',
    'icon': 'fa-car',
    'active': False,
    'categories': ['4bf58dd8d48988d113951735']
    },
    {
    'name': 'Kino',
    'icon': 'fa-film',
    'active': False,
    'categories': ['4bf58dd8d48988d17f941735']
    }
]


def get_filter_mapping():
    for fil in FILTERS:
        for cat in fil['categories']:
            yield cat, cat


def make_mapping(data, filters):
    filter_cats = get_filter_mapping()

    if not os.path.exists(DATA_PATH):
        logger.warn('data path not found: %s', DATA_PATH)
        return {}
    with open(DATA_PATH) as f:
        cats = json.load(f)['response']['categories']

    yield from _get_mapping(cats, filter_cats)


def _get_mapping(cats, filter_cats, parent=None):
    for cat in cats:
        parent = parent or cat['id']
        if cat['id'] in filter_cats:
            parent = cat['id']
        yield cat['id'], parent
        yield from _get_mapping(
            cat.get('categories', []),
            filter_cats,
            parent=parent
        )


# CATEGORY_MAPPING = dict(make_mapping(DATA_PATH, FILTERS))
CATEGORY_MAPPING = dict(get_filter_mapping())


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
    FILTERS = FILTERS

    def get_places(self, location=None, coordinates=None,
                   q=None, categories=None, radius=None, **kwargs):
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
        category = ''
        for cat in r['categories']:
            if cat['id'] in CATEGORY_MAPPING:
                category = CATEGORY_MAPPING[cat['id']]
                break

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
            'category': category
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
        result = response.json()['response']['venue']
        return self.extract_result(result)

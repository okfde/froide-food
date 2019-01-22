import os
import json

from django.conf import settings
from django.core.cache import cache

import requests
import logging

from .base import BaseVenueProvider, VenueProviderException


logger = logging.getLogger('froide')

SEARCH_URL = 'https://api.yelp.com/v3/businesses/search'
LOOKUP_URL = 'https://api.yelp.com/v3/businesses/{ident}'
API_KEY = settings.FROIDE_FOOD_CONFIG.get('api_key_yelp')

RELEVANT_TYPES = [
    'restaurants',
    'food',
    'servicestations'
]

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'categories.json')

FILTERS = [
    {
      'name': 'Fleischerei/Metzgerei',
      'icon': 'fa-paw',
      'active': False,
      'categories': ['meats', 'butcher']
    },
    {
      'name': 'Bäckerei/Konditorei',
      'icon': 'fa-pie-chart',
      'active': False,
      'categories': ['bakeries']
    },
    {
      'name': 'Restaurant/Gaststätte',
      'icon': 'fa-cutlery',
      'active': False,
      'categories': ['restaurants']
    },
    {
      'name': 'Café/Bar',
      'icon': 'fa-coffee',
      'active': False,
      'categories': ['coffee', 'bars']
    },
    {
      'name': 'Eisdiele',
      'icon': 'fa-child',
      'active': False,
      'categories': ['icecream']
    },
    {
      'name': 'Kiosk/Spätkauf',
      'icon': 'fa-beer',
      'active': False,
      'categories': ['kiosk']
    },
    {
      'name': 'Diskothek/Club',
      'icon': 'fa-diamond',
      'active': False,
      'categories': ['danceclubs']
    },
    {
      'name': 'Imbiss',
      'icon': 'fa-soccer-ball-o',
      'active': False,
      'categories': ['foodtrucks', 'foodstands']
    },
    {
      'name': 'Systemgastronomie',
      'icon': 'fa-bars',
      'active': False,
      'categories': ['hotdogs']
    },
    {
      'name': 'Hotel/Pension',
      'icon': 'fa-bed',
      'active': False,
      'categories': ['hotels', 'hostels']
    },
    {
      'name': 'Supermarkt/Discounter',
      'icon': 'fa-shopping-cart',
      'active': False,
      'categories': ['discountstore']
    },
    {
      'name': 'Einzelhandel',
      'icon': 'fa-shopping-basket',
      'active': False,
      'categories': ['grocery']
    },
    {
      'name': 'Tankstelle',
      'icon': 'fa-car',
      'active': False,
      'categories': ['servicestations']
    },
    {
      'name': 'Kino',
      'icon': 'fa-film',
      'active': False,
      'categories': ['movietheaters']
    }
    # // Fleischerei/Metzgerei
    # // Bäckerei/Konditorei
    # // Restaurant/Gaststätte
    # // Café/Bar
    # // Eisdiele
    # // Kiosk/Spätkauf
    # // Diskothek/Club
    # // Imbiss
    # // Systemgastronomie
    # // Hotel/Pension
    # // Supermarkt/Discounter
    # // Einzelhandel (Sonstige)
    # // Tankstelle
]


def make_mapping(category_path, filters):
    if not os.path.exists(category_path):
        logger.warn('data path not found: %s', category_path)
        return {}
    with open(category_path) as f:
        cats = json.load(f)

    filter_cats = []
    for fil in filters:
        filter_cats.extend(fil['categories'])

    return dict(_get_mapping(cats, filter_cats))


def _get_mapping(cats, filter_cats):
    for fc in filter_cats:
        yield fc, fc
    for cat in cats:
        for parent in cat['parents']:
            if parent in filter_cats:
                yield cat['alias'], parent


CATEGORY_MAPPING = make_mapping(DATA_PATH, FILTERS)


def make_cache_key(params, method='search'):
    keys = ('radius', 'latitude', 'longitude')
    return 'froide_food:yelp:%s:%s' % (
        method,
        '_'.join(
            str(params.get(key)) for key in keys
        )
    )


class YelpVenueProvider(BaseVenueProvider):
    name = 'yelp'
    FILTERS = FILTERS

    def get_places(self, location=None, coordinates=None,
                   q=None, categories=None, radius=None, **kwargs):
        params = {
            'radius': 10000,
            'limit': 50,
            'locale': 'de_DE'
        }
        can_cache = True
        if location is not None:
            can_cache = False
            params['location'] = location + ', Deutschland'
        else:
            params.update({
                'latitude': coordinates[0],
                'longitude': coordinates[1],
            })
        if q:
            can_cache = False
            params['term'] = q
        if categories:
            params['categories'] = ','.join(categories)
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
                headers={
                    'Authorization': 'Bearer %s' % API_KEY
                }
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

        if 'businesses' not in results:
            return []
        results = results['businesses']

        return [
            self.extract_result(r)
            for r in results
            if self.is_in_germany((
                r['coordinates']['longitude'],
                r['coordinates']['latitude'],
            ))
        ]

    def extract_result(self, r):
        cats = r['categories']
        category = None
        if cats:
            category = [CATEGORY_MAPPING.get(c['alias'], None) for c in cats]
            category = [c for c in category if c is not None]
        if category:
            category = category[0]
        else:
            category = None

        return {
            'ident': '%s:%s' % (self.name, r['id']),
            'lat': r['coordinates']['latitude'],
            'lng': r['coordinates']['longitude'],
            'name': r['name'],
            'address': ('%s\n%s %s' % (
                r['location']['address1'] or '',
                r['location']['zip_code'] or '',
                r['location']['city'] or ''
            )).strip(),
            'city': r['location']['city'],
            'image': r['image_url'].replace('o.jpg', 'l.jpg'),
            'rating': r.get('rating'),
            'review_count': r.get('review_count'),
            'url': r['url'],
            'category': category
        }

    def get_place(self, ident):
        if ident.startswith('yelp:'):
            ident = ident.replace('yelp:', '')
        response = requests.get(
            LOOKUP_URL.format(ident=ident),
            params={'locale': 'de_DE'},
            headers={
                'Authorization': 'Bearer %s' % API_KEY
            }
        )
        if response.status_code != 200:
            logger.warn('API response: %s - %s',
                        response.status_code, response.text)
            raise VenueProviderException()

        logger.info('API Request: %s (%s)',
                    response.request.url, response.status_code)
        result = response.json()
        return self.extract_result(result)

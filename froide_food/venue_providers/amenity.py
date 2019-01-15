import logging
from difflib import SequenceMatcher

from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from django_amenities.models import Amenity

from .base import BaseVenueProvider
from ..geocode import geocode, reverse_geocode
from ..utils import is_address_bad

logger = logging.getLogger('froide')


FILTERS = [
    {
        'name': 'Bäckerei/Konditorei',
        'icon': 'fa-pie-chart',
        'active': False,
        'categories': ['bakery']
    },
    {
        'name': 'Restaurant/Gaststätte',
        'icon': 'fa-cutlery',
        'active': False,
        'categories': ['restaurant']
    },
    {
        'name': 'Café',
        'icon': 'fa-coffee',
        'active': False,
        'categories': ['cafe']
    },
    {
        'name': 'Bar',
        'icon': 'fa-glass',
        'active': False,
        'categories': ['bar', 'pub']
    },
    {
        'name': 'Biergarten',
        'icon': 'fa-beer',
        'active': False,
        'categories': ['biergarten']
    },
    {
        'name': 'Eisdiele',
        'icon': 'fa-child',
        'active': False,
        'categories': ['ice_cream']
    },
    {
        'name': 'Kiosk/Spätkauf',
        'icon': 'fa-beer',
        'active': False,
        'categories': ['alcohol', 'beverages', 'kiosk']
    },
    {
        'name': 'Diskothek/Club',
        'icon': 'fa-diamond',
        'active': False,
        'categories': ['nightclub']
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
        'categories': ['fast_food', 'food_court']
    },
    {
        'name': 'Supermarkt/Discounter',
        'icon': 'fa-shopping-cart',
        'active': False,
        'categories': ['supermarket', 'convenience']
    },
    {
        'name': 'Einzelhandel',
        'icon': 'fa-shopping-basket',
        'active': False,
        'categories': ['department_store', 'wholesale', 'general']
    },
    {
        'name': 'Tankstelle',
        'icon': 'fa-car',
        'active': False,
        'categories': ['fuel']
    },
    {
        'name': 'Kino',
        'icon': 'fa-film',
        'active': False,
        'categories': ['cinema']
    }
]


def get_filter_mapping():
    for fil in FILTERS:
        for cat in fil['categories']:
            yield cat, cat


class AmenityVenueProvider(BaseVenueProvider):
    name = 'amenity'
    FILTERS = FILTERS

    def get_places(self, location=None, coordinates=None,
                   q=None, categories=None, radius=None):
        if location is not None:
            point, formatted_address = geocode(location, address=False)
        elif coordinates is not None:
            point = Point(coordinates[1], coordinates[0])

        if point is None:
            return []

        if radius is None:
            radius = 1000
        radius = max(10000, radius)

        results = (
            Amenity.objects
            .exclude(name='')
            .filter(geo__dwithin=(point, radius))
            .filter(geo__distance_lte=(point, D(m=radius)))
            .annotate(distance=Distance("geo", point))
            .order_by("distance")
        )
        if q is not None:
            results = results.filter(name__contains=q)

        results = results[:100]

        return [
            self.extract_result(r)
            for r in results
        ]

    def extract_result(self, r):
        return {
            'ident': '%s:%s' % (self.name, r.ident),
            'lat': r.geo.coords[1],
            'lng': r.geo.coords[0],
            'name': r.name,
            'address': r.address,
            'city': r.city,
            'category': r.amenity
        }

    def get_place(self, ident):
        if ident.startswith('amenity:'):
            ident = ident.replace('amenity:', '')
        pk = ident.split('_')[0]
        try:
            amenity = Amenity.objects.get(pk=pk)
            self.fix_address(amenity)
            return self.extract_result(amenity)
        except Amenity.DoesNotExist:
            return None

    def fix_address(self, amenity):
        address = amenity.address
        if not is_address_bad(address):
            return
        loc = amenity.geo.coords
        result = reverse_geocode([loc[1], loc[0]])
        if result is None:
            return
        raw = result.raw
        fixed = False
        fix_list = (
            ('street', 'text'),
            ('postcode', 'postcode'),
            ('housenumber', 'address'),
            ('city', 'place'),
        )
        for k, v in fix_list:
            try:
                if not getattr(amenity, k) and raw[v]:
                    fixed = True
                    setattr(amenity, k, raw[v])
            except KeyError:
                pass
        if fixed:
            amenity.save()

    def match_place(self, latlng, name):
        radius = 100
        point = Point(latlng[1], latlng[0])
        results = (
            Amenity.objects
            .filter(geo__dwithin=(point, radius))
            .filter(geo__distance_lte=(point, D(m=radius)))
            .annotate(distance=Distance("geo", point))
            .order_by("distance")
        )[:5]
        for r in results:
            ratio = SequenceMatcher(None, name, r.name).ratio()
            print('Checking', r.name, name, ratio)
            if ratio > 0.7:
                return r
        return None

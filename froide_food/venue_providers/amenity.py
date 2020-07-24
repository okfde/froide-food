import logging
from difflib import SequenceMatcher

from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from django_amenities.models import Amenity

from .base import BaseVenueProvider
from ..geocode import geocode, reverse_geocode
from ..utils import is_address_bad, normalize_name

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
    },
    {
        'name': 'Hotel',
        'icon': 'fa-bed',
        'active': False,
        'categories': ['hotel', 'hostel']
    }
]


def get_filter_mapping():
    for fil in FILTERS:
        for cat in fil['categories']:
            yield cat, cat


class AmenityVenueProvider(BaseVenueProvider):
    name = 'amenity'
    FILTERS = FILTERS
    ORDER_ZOOM_LEVEL = 15

    def get_queryset(self):
        return Amenity.objects.filter(topics__contains=['food'])

    def get_places(self, location=None, coordinates=None,
                   q=None, categories=None, radius=None, zoom=None):
        location_search = False
        if location is not None:
            location_search = True
            point, formatted_address = geocode(location, address=False)
        elif coordinates is not None:
            point = Point(coordinates[1], coordinates[0])

        if point is None:
            return []

        if radius is None:
            radius = 1000
        radius = max(min(10000, radius), 100)

        results = (
            self.get_queryset()
            .exclude(name='')
            .filter(geo__dwithin=(point, radius))
            .filter(geo__distance_lte=(point, D(m=radius)))
        )
        order_distance = zoom is None or zoom >= self.ORDER_ZOOM_LEVEL
        if not location_search and order_distance:
            results = (
                results
                .annotate(distance=Distance("geo", point))
                .order_by("distance")
            )
        else:
            results = results.order_by('?')

        if q is not None:
            results = results.filter(name__icontains=q.lower())

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
            'category': r.category
        }

    def get_object(self, ident):
        if ident.startswith('amenity:'):
            ident = ident.replace('amenity:', '')
        pk = ident.split('_')[0]
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            return None

    def get_place(self, ident):
        amenity = self.get_object(ident)
        if amenity is None:
            return None
        self.fix_address(amenity)
        return self.extract_result(amenity)

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
        radius_thresholds = (
            (30, 0.8),
            (20, 0.7),
            (10, 0.6)
        )

        point = Point(latlng[1], latlng[0])
        for radius, threshold in radius_thresholds:
            print('Trying with', radius, threshold)
            results = (
                Amenity.objects
                .filter(geo__dwithin=(point, radius))
                .filter(geo__distance_lte=(point, D(m=radius)))
                .annotate(distance=Distance("geo", point))
                .order_by("distance")
            )[:5]
            name = normalize_name(name)
            matches = list(
                rank_match_results(results, name, radius, threshold)
            )
            if matches:
                # Sort by ratio, highest first
                matches.sort(key=lambda x: x[0], reverse=True)
                return self.extract_result(matches[0][1])
        return None


def rank_match_results(results, name, radius, threshold):
    for r in results:
        if r.distance.m > radius:
            continue
        r_name = normalize_name(r.name)
        ratio = SequenceMatcher(None, name, r_name).ratio()
        print('Checking: ', r.name, ' | ', name, ratio)
        if ratio >= threshold:
            yield ratio, r

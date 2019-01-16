import uuid

from django.contrib.gis.measure import D

import logging

from ..models import VenueRequest
from ..geocode import geocode
from .base import BaseVenueProvider


logger = logging.getLogger('froide')


class CustomVenueProvider(BaseVenueProvider):
    name = 'custom'

    def create(self, data):
        point, formatted_address = geocode(data['address'])
        if point is None:
            return None

        if not self.is_in_germany(point.coords):
            return None

        matching_venues = VenueRequest.objects.filter(
            name__contains=data['name'],
            geo__isnull=False,
            geo__distance_lte=(point, D(m=10))
        )
        if matching_venues:
            venue = matching_venues[0]
        else:
            formatted_address = formatted_address.replace(', ', '\n')
            formatted_address = formatted_address.replace('\nGermany', '')
            formatted_address = formatted_address.replace('\nDeutschland', '')
            venue = VenueRequest.objects.create(
                ident='custom:%s' % uuid.uuid4(),
                name=data['name'],
                address=formatted_address,
                geo=point
            )

        place = venue.to_place()
        additional_data = self.get_detail(venue.ident, detail=False)
        place.update(additional_data)
        return place

    def add_extras(self, place, mapping):
        if place['ident'] in mapping:
            venue = mapping[place['ident']]
            place['name'] = venue.name
            place['address'] = venue.address
            place['lat'] = venue.geo.coords[1]
            place['lng'] = venue.geo.coords[0]

    def get_place(self, ident):
        venues = VenueRequest.objects.filter(ident=ident)
        if not venues:
            return None
        venue = venues[0]
        return {
            'ident': ident,
            'name': venue.name,
            'address': venue.address,
            'lat': venue.geo.coords[1],
            'lng': venue.geo.coords[0],
        }

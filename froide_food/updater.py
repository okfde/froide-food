from django_amenities.models import Amenity

from .models import VenueRequest
from .utils import (
    names_similar, merge_venues
)


class FoodUpdater:
    def get_used_osm_ids(self):
        idents = VenueRequest.objects.filter(
            ident__startswith='amenity:'
        ).values_list('ident', flat=True)
        return set(int(x.split(':')[1].split('_')[1]) for x in idents)

    def get_safe_update_osm_ids(self, used_existing_osm_ids):
        safe_update_osm_ids = set()
        for i, osm_id in enumerate(used_existing_osm_ids):
            if i % 1000 == 0:
                print('Progress ', i / len(used_existing_osm_ids) * 100, '%')
            amenity = Amenity.objects.get(osm_id=osm_id)
            ident = 'amenity:' + amenity.ident
            venues = VenueRequest.objects.filter(ident=ident)
            if len(venues) > 1:
                venue = merge_venues(venues)
            elif not venues:
                safe_update_osm_ids.add(osm_id)
                continue
            else:
                venue = venues[0]
            if venue.name != amenity.name:
                if not names_similar(venue.name, amenity.name):
                    print(venue.name, amenity.name,
                          venue.ident, amenity.osm_id)
                    continue
            safe_update_osm_ids.add(osm_id)
        return safe_update_osm_ids

import argparse
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation

from django_amenities.models import Amenity
from django_amenities.utils import (
    get_amenities, get_osm_id_set,
    create_amenities_bulk, update_amenities_bulk
)

from ...models import VenueRequest
from ...utils import (
    names_similar, merge_venues
)


def chunks(l, n):
    n = max(1, n)
    return (l[i:i+n] for i in range(0, len(l), n))


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):
    help = "Switch venue requests"

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('timestamp', type=valid_date)
        parser.add_argument('version', type=int, default=0, nargs='?')

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        version = options['version']
        self.stdout.write(
            'Starting update of {filename} with date {timestamp} at version {version}'.format(
                **options
            ))
        timestamp = options['timestamp']
        idents = VenueRequest.objects.filter(
            ident__startswith='amenity:'
        ).values_list('ident', flat=True)
        used_osm_ids = set(int(x.split(':')[1].split('_')[1]) for x in idents)
        existing_osm_ids = set(Amenity.objects.all().values_list(
            'osm_id', flat=True))
        existing_outdated_osm_ids = set(Amenity.objects.filter(
                version__lt=version).values_list(
            'osm_id', flat=True))
        current_osm_ids = get_osm_id_set(
            options['filename']
        )
        current_updated_osm_ids = get_osm_id_set(
            options['filename'], timestamp=timestamp
        )

        obsolete_osm_ids = existing_osm_ids - current_osm_ids
        # Remove these unused amenities:
        remove_osm_ids = list(obsolete_osm_ids - used_osm_ids)
        self.stdout.write('Removing {} obsolete amenities'.format(
            len(remove_osm_ids))
        )
        for chunk in chunks(remove_osm_ids, 100):
            Amenity.objects.filter(osm_id__in=chunk).delete()

        # Create these amenities
        fresh_osm_ids = current_osm_ids - existing_osm_ids

        self.stdout.write('Creating {} new amenities'.format(
            len(fresh_osm_ids))
        )
        fresh_amenities = get_amenities(
            options['filename'], version=version, osm_ids=fresh_osm_ids
        )
        for progress in create_amenities_bulk(fresh_amenities):
            self.stdout.write('Batch-progress %s' % progress)

        self.stdout.write('Done')
        # Match with VenueRequests,  maybe run later
        # non_amenity_venues = VenueRequest.objects.exclude(
        #     ident__startswith='amenity:'
        # )
        # self.stdout.write('Matching {} non-amenity with new amenities'.format(
        #     non_amenity_venues.count()))
        # for venue in non_amenity_venues:
        #     match_venue_with_provider(venue, 'amenity', allow_failed=True)

        # Update these amenities
        update_osm_ids = current_updated_osm_ids & existing_outdated_osm_ids
        direct_update_osm_ids = update_osm_ids - used_osm_ids
        self.stdout.write('Updating existing unused {} amenities'.format(
            len(direct_update_osm_ids))
        )
        updated_amenities = get_amenities(
            options['filename'], version=version, osm_ids=direct_update_osm_ids
        )
        for progress in update_amenities_bulk(updated_amenities):
            self.stdout.write('Batch-progress %s' % progress)

        used_existing_osm_ids = update_osm_ids & used_osm_ids

        self.stdout.write('Checking existing used {} amenities'.format(
            len(used_existing_osm_ids))
        )

        safe_update_osm_ids = set()
        for i, osm_id in enumerate(used_existing_osm_ids):
            if i % 1000 == 0:
                print('Progress ', i / len(used_existing_osm_ids) * 100, '%')
            amenity = Amenity.objects.get(osm_id=osm_id)
            ident = 'amenity:' + amenity.ident
            venues = VenueRequest.objects.filter(ident=ident)
            if len(venues) > 1:
                venue = merge_venues(venues)
            else:
                venue = venues[0]
            if venue.name != amenity.name:
                if not names_similar(venue.name, amenity.name):
                    print(venue.name, amenity.name,
                          venue.ident, amenity.osm_id)
                    continue
            safe_update_osm_ids.add(osm_id)

        self.stdout.write('Update existing used safe {} amenities'.format(
            len(safe_update_osm_ids))
        )
        safe_updated_amenities = get_amenities(
            options['filename'], version=version, osm_ids=safe_update_osm_ids
        )
        for progress in update_amenities_bulk(safe_updated_amenities):
            self.stdout.write('Batch-progress %s' % progress)

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation
from django.db.models import Q
from django.contrib.gis.geos import Point

from geopy.distance import distance as geopy_distance

from ...models import VenueRequest
from ...utils import get_name_and_address
from ...geocode import geocode
from ...venue_providers import venue_providers


class Command(BaseCommand):
    help = "Switch venue requests"

    def add_arguments(self, parser):
        parser.add_argument('provider', type=str)

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGE_CODE)

        provider = options['provider']

        venues = VenueRequest.objects.exclude(
            Q(ident__startswith=provider)
            | Q(ident__startswith='custom')
        )
        for venue in venues:
            if not venue.context:
                venue.context = {}
            if venue.context.get('failed_' + provider):
                return
            print('Trying venue', venue)
            result = self.match_venue_with_provider(venue, provider)
            if not result:
                venue.context['failed_' + provider] = True
                venue.save()

        self.stdout.write("Import done.\n")

    def match_venue_with_provider(self, venue, provider):
        if venue.ident.startswith(provider):
            return True
        if venue.context.get('failed_' + provider):
            return False
        if provider in venue.context:
            current, current_id = venue.ident.split(':', 1)
            venue.context[current] = current_id
            venue.ident = provider + ':' + venue.context[provider]
            venue.save()
            return True
        info = get_name_and_address(venue)
        if not info:
            return False
        address = ', '.join(info['address'])
        point, formatted_address = geocode(address)
        if not point:
            return False
        venue_provider = venue_providers[provider]
        places = venue_provider.get_places(coordinates=[
            point.coords[1],
            point.coords[0]
        ], radius=200, q=info['name'])
        if not places:
            return False
        place = places[0]
        place['lat']
        place_point = Point(place['lng'], place['lat'])
        distance = geopy_distance(place_point, point)
        if distance.meters > 200:
            return False
        venue.context[provider] = place['ident'].split(':', 1)[1]
        current, current_id = venue.ident.split(':', 1)
        venue.context[current] = current_id
        venue.ident = provider + ':' + venue.context[provider]
        venue.save()
        return True

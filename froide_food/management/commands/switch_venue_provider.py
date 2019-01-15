from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import translation
from django.db.models import Q

from ...models import VenueRequest
from ...utils import match_venue_with_provider


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
            result = match_venue_with_provider(venue, provider)
            if result:
                print('Success')
            # if not result:
            #     venue.context['failed_' + provider] = True
            #     venue.save()

        self.stdout.write("Import done.\n")

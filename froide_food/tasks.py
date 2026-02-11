from datetime import timedelta
import logging
from django.utils import timezone
from froide.celery import app as celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def depublish_old_reports_task():
    from .utils import depublish_old_reports

    depublish_old_reports()


@celery_app.task
def update_google_venues(max_days: int = 0) -> None:
    """
    This tasks updates Google venue ids, since they can change.
    Only venues with requests made earlier than 30 days ago will be checked.
    If the venue cannot be found anymore, new requests will be disallowed.
    This should be set up as a periodic task.

    :param max_days: Specify how far into the past venues should be checked. Set this to the interval of the periodic task.
    """

    from .models import VenueRequest
    from .venue_providers.google import GoogleVenueProvider
    from .venue_providers import VenueProviderException

    g = GoogleVenueProvider()

    now = timezone.now()

    venues = VenueRequest.objects.filter(
        ident__startswith="google:", last_request__lt=now - timedelta(days=30)
    )

    if max_days != 0:
        venues.filter(last_request__gt=now - timedelta(days=max_days))

    updated = []

    for venue in venues:
        try:
            ident = g.get_place_ident(venue.ident)

            if venue.ident != ident:
                old_ident = venue.ident
                venue.ident = ident
                updated.append(venue)
                logger.info(
                    f"Updated venue request {venue.id} ident from {old_ident} to {ident}"
                )
        except VenueProviderException:
            venue.rerequestable = False
            updated.append(venue)
            logger.info(f"Disallowed new venue requests for {venue.id}")

    VenueRequest.objects.bulk_update(updated, ["rerequestable", "ident"])

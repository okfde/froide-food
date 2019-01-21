import json

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FroideFoodConfig(AppConfig):
    name = 'froide_food'
    verbose_name = _("Froide Food App")

    def ready(self):
        from .listeners import (
            connect_request_object,
            connect_request_status_changed
        )
        from froide.foirequest.models import FoiRequest
        from froide.account.export import registry

        registry.register(export_user_data)

        FoiRequest.request_created.connect(connect_request_object)
        FoiRequest.status_changed.connect(connect_request_status_changed)

        from froide.helper import api_router

        from .api_views import VenueViewSet

        api_router.register(
            r'venue',
            VenueViewSet,
            basename='venue'
        )


def export_user_data(user):
    from froide.foirequest.models.request import get_absolute_domain_short_url
    from .models import VenueRequestItem

    venue_requests = (
        VenueRequestItem.objects
        .filter(foirequest__user=user)
        .select_related('venue')
    )
    if not venue_requests:
        return
    yield ('venue_requests.json', json.dumps([
        {
            'venue': v.venue.to_place(),
            'timestamp': v.timestamp.isoformat(),
            'request': get_absolute_domain_short_url(v.foirequest_id)
        }
        for v in venue_requests]).encode('utf-8')
    )

# -*- encoding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FroideFoodConfig(AppConfig):
    name = 'froide_food'
    verbose_name = _("Froide Food App")

    def ready(self):
        from .listeners import connect_request_object
        from froide.foirequest.models import FoiRequest

        FoiRequest.request_created.connect(connect_request_object)

        from froide.helper import api_router

        from .api_views import VenueViewSet

        api_router.register(
            r'venue',
            VenueViewSet,
            base_name='venue'
        )

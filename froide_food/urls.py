from django.urls import path
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page

from froide.api import api_router

from .api_views import VenueViewSet
from .views import (
    index,
    embed,
    make_request,
    stats,
    osm_help,
    show_reports,
    requests_in_region,
)


api_router.register(r"venue", VenueViewSet, basename="venue")

urlpatterns = [
    path("", index, name="food-index"),
    path("embed/", embed, name="food-embed"),
    path("_stats/", stats, name="food-stats"),
    path("_reports/", show_reports, name="food-report"),
    path("osm-hilfe/", osm_help, name="food-osm_help"),
    path("region/<slug>/", requests_in_region, name="food-requests_in_region"),
    path("anfragen/", make_request, name="food-make_request"),
    path(
        "sw.js",
        cache_page(None)(
            TemplateView.as_view(
                template_name="froide_food/sw.js", content_type="application/javascript"
            )
        ),
        name="food-service_worker",
    ),
]

from django.urls import path
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page

from .views import (
    index, embed, make_request
)

urlpatterns = [
    path('', index, name='food-index'),
    path('embed/', embed, name='food-embed'),
    path('anfragen/', make_request, name='food-make_request'),
    path('sw.js', cache_page(None)(TemplateView.as_view(
        template_name='froide_food/sw.js',
        content_type='application/javascript')), name='food-service_worker'),
]

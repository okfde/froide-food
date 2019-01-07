from django.urls import path
from django.views.generic import TemplateView

from .views import (
    index, embed, make_request
)

urlpatterns = [
    path('', index, name='food-index'),
    path('embed/', embed, name='food-embed'),
    path('anfragen/', make_request, name='food-make_request'),
    path('sw.js', TemplateView.as_view(
        template_name='froide_food/sw.js',
        content_type='application/javascript'), name='food-service_worker'),
]

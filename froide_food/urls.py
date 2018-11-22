from django.conf.urls import url
from django.views.generic import TemplateView

from .views import (
    index, embed, make_request
)

urlpatterns = [
    url(r'^$', index, name='food-index'),
    url(r'^embed/$', embed, name='food-embed'),
    url(r'^anfragen/$', make_request, name='food-make_request'),
    url(r'^sw.js', TemplateView.as_view(
        template_name='froide_food/sw.js',
        content_type='application/javascript'), name='food-service_worker'),
]

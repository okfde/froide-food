from django.conf.urls import url

from .views import (
    index, make_request
)

urlpatterns = [
    url(r'^$', index, name='food-index'),
    url(r'^anfragen/$', make_request, name='food-make_request'),
]

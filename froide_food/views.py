import json

from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages

from froide.foirequest.views import MakeRequestView
from froide.helper.utils import get_redirect

from .venue_providers import venue_provider, venue_providers
from .utils import (
    get_city_from_request, make_request_url, get_request_count,
    get_hygiene_publicbody, MAX_REQUEST_COUNT
)


def get_food_map_config(request, embed):
    city = get_city_from_request(request)

    return {
        'city': city or {},
        'filters': venue_provider.FILTERS,
        'embed': embed,
        'requestUrl': '{}{}'.format(
            settings.SITE_URL, reverse('food-make_request')
        ),
        'staticUrl': settings.STATIC_URL,
        'appUrl': settings.SITE_URL + reverse('food-index'),
        'swUrl': reverse('food-service_worker'),
    }


def index(request, base_template='froide_food/base.html', embed=False):

    fake_make_request_view = MakeRequestView(request=request)

    context = {
        'base_template': base_template,
        'config': json.dumps(get_food_map_config(request, embed)),
        'request_form': fake_make_request_view.get_form(),
        'user_form': fake_make_request_view.get_user_form(),
        'request_config': json.dumps(fake_make_request_view.get_js_context())
    }

    return render(request, 'froide_food/index.html', context)


@xframe_options_exempt
def embed(request):
    return index(
        request,
        base_template='froide_food/embed_base.html',
        embed=True
    )


def make_request(request):
    ident = request.GET.get('ident')
    if not ident:
        messages.add_message(request, messages.ERROR, 'Fehlerhafter Link')
        return redirect('food-index')
    try:
        provider, _ = ident.split(':')
        if provider not in venue_providers:
            raise ValueError
    except ValueError:
        messages.add_message(request, messages.ERROR, 'Fehlerhafter Link')
        return redirect('food-index')

    place = venue_providers[provider].get_place(ident, detail=True)

    return get_redirect(request, default='food-index', params={
        'query': place['name'],
        'latlng': '{},{}'.format(place['lat'], place['lng']),
        'ident': ident
    })


def old_make_request(request, place, ident):
    try:
        pb = get_hygiene_publicbody(place['lat'], place['lng'])
    except ValueError as e:
        messages.add_message(request, messages.ERROR, str(e))
        return redirect('food-index')

    url = make_request_url(place, pb)

    stopper = False
    request_count = 0
    if request.user.is_authenticated:
        request_count = get_request_count(request, pb)
        if request_count >= MAX_REQUEST_COUNT:
            stopper = True

    if stopper or request.GET.get('stopper') is not None:
        return get_redirect(request, default='food-index', params={
            'query': place['name'],
            'latlng': '{},{}'.format(place['lat'], place['lng']),
            'ident': ident
        })

    return redirect(url)

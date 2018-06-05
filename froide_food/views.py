import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_exempt

from .venue_providers import venue_providers, venue_provider
from .utils import (
    get_hygiene_publicbody, make_request_url, get_city_from_request
)


def index(request, base_template='froide_food/base.html', extra_context=None):
    city = get_city_from_request(request)
    context = {
        'base_template': base_template,
        'city': json.dumps(city or {}),
        'filters': json.dumps(venue_provider.FILTERS)
    }
    if extra_context is not None:
        context.update(extra_context)
    return render(request, 'froide_food/index.html', context)


@xframe_options_exempt
def embed(request):
    return index(
        request,
        base_template='froide_food/embed_base.html',
        extra_context={
            'embed': True
        }
    )


def make_request(request):
    ident = request.GET.get('ident')
    if not ident:
        messages.add_message(request, messages.ERROR, 'Fehlerhafter Link')
        return redirect('food-index')
    try:
        provider, ident = ident.split(':')
        if provider not in venue_providers:
            raise ValueError
    except ValueError:
        messages.add_message(request, messages.ERROR, 'Fehlerhafter Link')
        return redirect('food-index')

    place = venue_providers[provider].get_place(ident)
    try:
        pb = get_hygiene_publicbody(place['lat'], place['lng'])
    except ValueError as e:
        messages.add_message(request, messages.ERROR, str(e))
        return redirect('food-index')

    url = make_request_url(place, pb)
    return redirect(url)

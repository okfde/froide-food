import json
from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.urls import reverse
from django.conf import settings

from froide.foirequest.models import FoiRequest
from froide.foirequest.views import MakeRequestView

from .venue_providers import venue_providers, venue_provider
from .utils import (
    get_hygiene_publicbody, make_request_url, get_city_from_request,
    get_social_url, get_social_text
)


TIME_PERIOD = timedelta(days=90)
MAX_REQUEST_COUNT = 3


def get_dir_for_url(url):
    return '/'.join(url.split('/')[:-1]) + '/'


def get_food_map_config(city, embed):
    return {
      'city': city or {},
      'filters': venue_provider.FILTERS,
      'embed': embed,
      'requestUrl': '{}{}'.format(
          settings.SITE_URL, reverse('food-make_request')
        )
    }


def index(request, base_template='froide_food/base.html', embed=False):
    city = get_city_from_request(request)

    fake_make_request_view = MakeRequestView(request=request)

    context = {
        'base_template': base_template,
        'config': json.dumps(get_food_map_config(city, embed)),
        'request_form': fake_make_request_view.get_form(),
        'request_config': json.dumps(fake_make_request_view.get_js_context())
    }

    if not request.user.is_authenticated:
        context['user_form'] = fake_make_request_view.get_user_form()

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

    stopper = False
    request_count = 0
    if request.user.is_authenticated:
        request_count = FoiRequest.objects.filter(
            public_body=pb,
            user=request.user,
            first_message__gte=timezone.now() - TIME_PERIOD
        ).count()
        if request_count >= MAX_REQUEST_COUNT:
            stopper = True

    social_url = get_social_url(ident)
    social_text = get_social_text(ident, place)

    if stopper or request.GET.get('stopper') is not None:
        return render(request, 'froide_food/recommend.html', {
            'publicbody': pb,
            'request_count': request_count,
            'days': TIME_PERIOD.days,
            'max_count': MAX_REQUEST_COUNT,
            'social_url': social_url,
            'social_text': social_text,
            'url': url,
            'place': place
        })

    return redirect(url)

from django.conf import settings
# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import cache_page
from django.contrib.gis.geos import Point

from rest_framework import serializers, viewsets, status
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework.decorators import action

from froide.publicbody.api_views import PublicBodySerializer
from froide.foirequest.api_views import throttle_action
from froide.georegion.models import GeoRegion

from .venue_providers import (
    venue_provider, venue_providers, VenueProviderException
)
from .utils import (
    get_hygiene_publicbodies, make_request_url, get_request_count
)


class VenueRequestDocumentSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.CharField()


class VenueRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    url = serializers.CharField()
    status = serializers.CharField()
    resolution = serializers.CharField()
    timestamp = serializers.DateTimeField()
    documents = VenueRequestDocumentSerializer(many=True)


class VenueSerializer(serializers.Serializer):
    ident = serializers.CharField()
    lat = serializers.FloatField(required=False)
    lng = serializers.FloatField(required=False)
    name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    image = serializers.CharField(required=False)
    url = serializers.CharField(required=False)
    rating = serializers.FloatField(required=False)
    review_count = serializers.FloatField(required=False)
    category = serializers.CharField(required=False)
    last_status = serializers.CharField(required=False)
    last_resolution = serializers.CharField(required=False)
    last_request = serializers.DateTimeField(required=False)
    custom = serializers.BooleanField(required=False, default=False)

    requests = VenueRequestSerializer(many=True)
    publicbody = PublicBodySerializer(required=False)
    makeRequestURL = serializers.CharField(required=False)
    userRequestCount = serializers.IntegerField(required=False)


def get_lat_lng(request):
    try:
        lat = float(request.GET.get('lat'))
    except (ValueError, TypeError):
        raise ValueError
    try:
        lng = float(request.GET.get('lng'))
    except (ValueError, TypeError):
        raise ValueError
    return lat, lng


class CreateVenueThrottle(UserRateThrottle):
    scope = 'food-createvenue'
    THROTTLE_RATES = {
        scope: '10/day',
    }


class VenueViewSet(viewsets.ViewSet):
    permission_classes = ()

    @action(detail=False, methods=['get'])
    def extra_info_for_point(self, request):
        try:
            lat = float(request.GET.get('lat'))
        except (ValueError, TypeError):
            raise ValueError
        try:
            lng = float(request.GET.get('lng'))
        except (ValueError, TypeError):
            raise ValueError
        if lat and lng:
            pankow = GeoRegion.objects.filter(name="Pankow",
                                              part_of__name="Berlin",
                                              kind="borough")
            point = Point(lng, lat)
            if pankow.first().geom.covers(point):
                return Response({
                    'extra_info': 'Pankow veröffentlicht seine Kontrollberichte!',
                    'url': 'https://pankow.lebensmittel-kontrollergebnisse.de/'
                })
        return Response({})


    # @method_decorator(cache_page(60*5))
    def list(self, request):
        location = request.GET.get('location')
        if location:
            location_kwargs = {'location': location}
        else:
            try:
                lat, lng = get_lat_lng(request)
            except ValueError:
                return Response([])
            location_kwargs = {'coordinates': (lat, lng)}

        zoom = None
        if request.GET.get('zoom'):
            try:
                zoom = int(request.GET['zoom'])
            except ValueError:
                zoom = None
        location_kwargs['zoom'] = zoom

        try:
            radius = int(request.GET.get('radius'))
        except (ValueError, TypeError):
            radius = 10000

        query = request.GET.get('q')
        categories = request.GET.getlist('categories', [])

        current_provider = venue_provider

        only_requested = request.GET.get('requested', '') == '1'
        if only_requested:
            current_provider = venue_providers['requested']

        try:
            places = current_provider.search_places(
                q=query,
                radius=radius,
                categories=categories,
                **location_kwargs
            )
        except VenueProviderException:
            return Response({'results': [], 'error': True})

        serializer = VenueSerializer(places, many=True)

        return Response({'results': serializer.data, 'error': False})

    def retrieve(self, request, pk=None):
        if pk is None:
            return Response({'result': None, 'error': True})
        if ':' not in pk:
            return Response({'result': None, 'error': True})
        provider, _ = pk.split(':', 1)
        try:
            provider = venue_providers[provider]
        except KeyError:
            return Response({'result': None, 'error': True})

        try:
            lat, lng = get_lat_lng(request)
            name = request.GET['name']
            address = request.GET['address']
            place = provider.get_detail(pk, info={
                'name': name,
                'address': address,
                'city': request.GET.get('city'),
                'lat': lat,
                'lng': lng,
            })
        except (ValueError, KeyError):
            place = provider.get_detail(pk, detail=True)
        except VenueProviderException:
            place = None

        if place is None:
            return Response({'result': None, 'error': True})

        try:
            pbs = get_hygiene_publicbodies(
                place['lat'], place['lng']
            ).prefetch_related(
                'classification',
                'jurisdiction',
                'categories',
                'laws',
                'laws__combined'
            )
            place['publicbody'] = pbs[0]
            place['userRequestCount'] = get_request_count(
                request, place['publicbody']
            )
            url = settings.SITE_URL + make_request_url(place, pbs[0])
            place['makeRequestURL'] = url
        except (ValueError, IndexError):
            pass

        serializer = VenueSerializer(place, context={'request': request})
        return Response({'result': serializer.data, 'error': False})

    @throttle_action((CreateVenueThrottle,))
    def create(self, request, *args, **kwargs):
        serializer = VenueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        place = self.perform_create(serializer)
        if place is None:
            return Response(
                {'result': None, 'error': True},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = VenueSerializer(place, context={'request': request})
        return Response(
            {'result': serializer.data, 'error': False},
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        data = serializer.validated_data
        provider = venue_providers['custom']
        venue = provider.create(data)
        return venue

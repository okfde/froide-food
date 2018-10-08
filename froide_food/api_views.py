from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response

from froide.publicbody.api_views import PublicBodySerializer

from .venue_providers import (
    venue_provider, venue_providers, VenueProviderException
)
from .utils import get_hygiene_publicbodies, make_request_url


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
    image = serializers.CharField(required=False)
    url = serializers.CharField(required=False)
    rating = serializers.FloatField(required=False)
    review_count = serializers.FloatField(required=False)
    category = serializers.CharField(required=False)
    last_status = serializers.CharField(required=False)
    last_resolution = serializers.CharField(required=False)
    last_request = serializers.DateTimeField(required=False)

    requests = VenueRequestSerializer(many=True)
    publicbody = PublicBodySerializer(required=False)
    makeRequestURL = serializers.CharField(required=False)

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


class VenueViewSet(viewsets.ViewSet):
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

        try:
            radius = int(request.GET.get('radius'))
        except (ValueError, TypeError):
            radius = 10000

        query = request.GET.get('q')
        categories = request.GET.getlist('categories', [])

        try:
            places = venue_provider.search_places(
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
        provider, ident = pk.split(':', 1)
        provider = venue_providers[provider]

        try:
            lat, lng = get_lat_lng(request)
            name = request.GET['name']
            city = request.GET['city']
            address = request.GET['address']
            place = provider.get_detail(ident, detail=False)
            place['name'] = name
            place['city'] = city
            place['address'] = address
            place['lat'] = lat
            place['lng'] = lng
        except (ValueError, KeyError):
            place = provider.get_detail(ident, detail=True)

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
            place['makeRequestURL'] = make_request_url(place, pbs[0])
        except (ValueError, IndexError):
            pass

        serializer = VenueSerializer(place, context={'request': request})
        return Response({'result': serializer.data, 'error': False})

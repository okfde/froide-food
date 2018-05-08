from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response

from .venue_providers import venue_provider


class VenueSerializer(serializers.Serializer):
    ident = serializers.CharField()
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    name = serializers.CharField()
    address = serializers.CharField()
    image = serializers.CharField()
    url = serializers.CharField()
    rating = serializers.FloatField()


class VenueViewSet(viewsets.ViewSet):
    def list(self, request):
        try:
            lat = float(request.GET.get('lat'))
        except (ValueError, TypeError):
            return Response([])
        try:
            lng = float(request.GET.get('lng'))
        except (ValueError, TypeError):
            return Response([])

        try:
            radius = int(request.GET.get('radius'))
        except (ValueError, TypeError):
            radius = 10000

        query = request.GET.get('q')
        categories = request.GET.getlist('categories', [])

        places = venue_provider.search_places(
            (lat, lng),
            q=query,
            radius=radius,
            categories=categories
        )
        serializer = VenueSerializer(places, many=True)

        return Response(serializer.data)

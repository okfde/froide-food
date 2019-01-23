from django.db.models import Prefetch

from ..models import VenueRequest, VenueRequestItem

from .amenity import AmenityVenueProvider


class RequestedVenueProvider(AmenityVenueProvider):
    def get_queryset(self):
        qs = VenueRequest.objects.filter(last_request__isnull=False)
        vris = VenueRequestItem.objects.select_related('foirequest')
        qs = qs.prefetch_related(
            Prefetch('request_items', queryset=vris)
        )
        return qs

    def search_places(self, *args, **kwargs):
        places = self.get_places(*args, **kwargs)
        return places

    def extract_result(self, venue):
        return venue.to_place(with_requests=True)

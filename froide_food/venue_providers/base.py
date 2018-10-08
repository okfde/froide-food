from collections import defaultdict
from django.db.models import Prefetch

from froide.foirequest.models import FoiAttachment

from ..models import VenueRequest, VenueRequestItem


class VenueProviderException(Exception):
    pass


class BaseVenueProvider(object):
    def search_places(self, *args, **kwargs):
        places = self.get_places(*args, **kwargs)
        mapping = self.get_venue_mapping_for_places(places)
        for p in places:
            self.add_requests(p, mapping)
        return places

    def get_venue_mapping_for_places(self, places):
        ident_list = [p['ident'] for p in places]
        qs = VenueRequest.objects.filter(ident__in=ident_list)
        vris = VenueRequestItem.objects.select_related('foirequest')
        qs = qs.prefetch_related(
            Prefetch('request_items', queryset=vris)
        )
        return {r.ident: r for r in qs}

    def get_detail(self, ident, detail=False):
        place = {
            'ident': '%s:%s' % (self.name, ident)
        }
        if detail:
            place = self.get_place(ident)
        mapping = self.get_venue_mapping_for_places([place])
        self.add_requests(place, mapping)

        attachments = FoiAttachment.objects.filter(
            approved=True,
            belongs_to__request__in=[
                vri.foirequest
                for venue in mapping.values()
                for vri in venue.request_items.all()
                if vri.foirequest is not None
            ]
        ).select_related('belongs_to', 'belongs_to__request')

        attachment_mapping = defaultdict(list)
        for a in attachments:
            attachment_mapping[a.belongs_to.request.pk].append(a)

        for req in place['requests']:
            self.add_documents(req, attachment_mapping)

        return place

    def add_requests(self, place, mapping):
        if place['ident'] in mapping:
            venue = mapping[place['ident']]
            place['last_status'] = venue.last_status
            place['last_resolution'] = venue.last_resolution
            place['last_request'] = venue.last_request
            fr = venue.last_request
            if fr is not None:
                place['requests'] = [{
                    'id': vri.foirequest.pk,
                    'url': vri.foirequest.get_absolute_url(),
                    'status': vri.foirequest.status,
                    'resolution': vri.foirequest.resolution,
                    'timestamp': vri.timestamp,
                    'documents': []
                } for vri in venue.request_items.all()]
            else:
                place['requests'] = []
        else:
            place['requests'] = []

    def add_documents(self, req, attachment_mapping):
        req['documents'] = [{
            'name': att.name,
            'url': att.get_absolute_domain_url(),
        } for att in attachment_mapping[req['id']]]

from collections import defaultdict

from django.db.models import Prefetch, Q
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point

from froide.foirequest.models import FoiAttachment
from froide.georegion.models import GeoRegion

from ..models import VenueRequest, VenueRequestItem
from ..utils import get_city, is_address_bad


class VenueProviderException(Exception):
    pass


class BaseVenueProvider(object):
    bounds = None

    def search_places(self, *args, **kwargs):
        places = self.get_places(*args, **kwargs)
        mapping = self.get_venue_mapping_for_places(places, **kwargs)
        others = set(mapping) - set(p['ident'] for p in places)
        places = places + [
            mapping[o].to_place() for o in others
        ]
        for p in places:
            self.add_requests(p, mapping)
        return places

    def is_in_germany(self, coords):
        if self.bounds is None:
            try:
                region = GeoRegion.objects.get(
                    name='Deutschland', level=0, kind='country'
                )
                self.bounds = region.geom.prepared
            except GeoRegion.DoesNotExist:
                self.bounds = False
        if not self.bounds:
            return True
        point = Point(*coords)
        return self.bounds.covers(point)

    def get_venue_mapping_for_places(self, places,
                                     coordinates=None, radius=None, **kwargs):
        ident_list = [p['ident'] for p in places]
        qs = VenueRequest.objects.filter(ident__in=ident_list)

        if coordinates is not None:
            point = Point(coordinates[1], coordinates[0])
            radius = radius or 500
            qs = qs.union(
                VenueRequest.objects
                .exclude(ident__startswith=self.name+':')
                .filter(geo__isnull=False)
                .filter(geo__dwithin=(point, radius))
                .filter(
                    geo__distance_lte=(point, D(m=radius))
                )[:50]
            )

        vris = VenueRequestItem.objects.select_related('foirequest')
        qs = qs.prefetch_related(
            Prefetch('request_items', queryset=vris)
        )
        return {r.ident: r for r in qs}

    def match_place(self, latlng, name):
        places = self.get_places(
            coordinates=latlng, radius=100,
            q=name
        )
        if not places:
            return None
        return places[0]

    def get_detail(self, ident, detail=False, info=None):
        place = {
            'ident': ident
        }
        if info:
            try:
                place['name'] = info['name']
                place['address'] = info['address']
                place['lat'] = info['lat']
                place['lng'] = info['lng']
                place['city'] = get_city(place)
            except KeyError:
                detail = True

        if not place.get('address') or is_address_bad(place['address']):
            detail = True

        if detail:
            place = self.get_place(ident)

        mapping = self.get_venue_mapping_for_places([place])
        self.add_extras(place, mapping)
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

    def add_extras(self, place, mapping):
        pass

    def add_requests(self, place, mapping):
        if place['ident'] in mapping:
            venue = mapping[place['ident']]
            place['last_status'] = venue.last_status
            place['last_resolution'] = venue.last_resolution
            place['last_request'] = venue.last_request
            fr = venue.last_request
            if fr is not None:
                vris = venue.request_items.filter(foirequest__isnull=False)
                place['requests'] = [to_vri(vri) for vri in vris]
            else:
                place['requests'] = []
        else:
            place['requests'] = []

    def add_documents(self, req, attachment_mapping):
        req['documents'] = [{
            'name': att.name,
            'url': att.get_absolute_domain_url(),
        } for att in attachment_mapping[req['id']]]


def to_vri(vri):
    if vri.foirequest.is_public():
        return {
            'id': vri.foirequest.pk,
            'url': vri.foirequest.get_absolute_url(),
            'status': vri.foirequest.status,
            'resolution': vri.foirequest.resolution,
            'timestamp': vri.timestamp,
            'documents': []
        }
    return {
        'id': None,
        'url': '',
        'status': vri.foirequest.status,
        'resolution': vri.foirequest.resolution,
        'timestamp': vri.timestamp,
        'documents': []
    }

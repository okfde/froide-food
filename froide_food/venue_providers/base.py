from ..models import VenueRequest


class BaseVenueProvider(object):
    def search_places(self, *args, **kwargs):
        places = self.get_places(*args, **kwargs)
        ident_list = [p['ident'] for p in places]
        qs = VenueRequest.objects.filter(ident__in=ident_list)
        qs = qs.select_related('foirequest')
        fvr = {r.ident: r for r in qs}
        for p in places:
            p['request_url'] = None
            p['request_status'] = None
            p['request_timestamp'] = None
            if p['ident'] in fvr:
                fr = fvr[p['ident']].foirequest
                p['request_url'] = fr.get_absolute_url()
                p['request_status'] = fr.status
                p['request_timestamp'] = fr.first_message
        return places

from ..models import VenueRequest


class BaseVenueProvider(object):
    def search_places(self, *args, **kwargs):
        places = self.get_places(*args, **kwargs)
        ident_list = [p['ident'] for p in places]
        qs = VenueRequest.objects.filter(ident__in=ident_list)
        qs = qs.select_related('foirequest')
        fvr = {r.ident: r for r in qs}
        for p in places:
            if p['ident'] in fvr:
                p['request'] = fvr[p['ident']].foirequest.get_absolute_url()
        return places

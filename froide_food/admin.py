from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin

from froide.foirequest.models import FoiRequest
from froide.helper.admin_utils import make_nullfilter

from .models import VenueRequest, VenueRequestItem


class VenueRequestItemInlineAdmin(admin.StackedInline):
    model = VenueRequestItem
    raw_id_fields = ('venue', 'foirequest', 'publicbody',)


class VenueRequestAdmin(LeafletGeoAdmin):
    inlines = [
        VenueRequestItemInlineAdmin
    ]
    date_hierarchy = 'last_request'
    list_filter = (
        'last_status', 'last_resolution',
        make_nullfilter('last_request', 'Hat Anfrage'),
        make_nullfilter('geo', 'Hat eigene Koordinate')
    )
    list_display = (
        'name', 'last_request',
        'get_last_status_display', 'get_last_resolution_display',
        'get_provider'
    )
    search_fields = ('name', 'ident')

    def get_last_status_display(self, obj):
        return FoiRequest.STATUS_RESOLUTION_DICT.get(
            obj.last_status, (obj.last_status,)
        )[0]
    get_last_status_display.short_description = 'letzter Status'

    def get_provider(self, obj):
        return obj.ident.split(':')[0]
    get_provider.short_description = 'provider'

    def get_last_resolution_display(self, obj):
        return FoiRequest.STATUS_RESOLUTION_DICT.get(
            obj.last_resolution, (obj.last_resolution,)
        )[0]
    get_last_resolution_display.short_description = 'letztes Ergebnis'


admin.site.register(VenueRequest, VenueRequestAdmin)

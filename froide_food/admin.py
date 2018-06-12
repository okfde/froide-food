from django.contrib import admin

from .models import VenueRequest, VenueRequestItem


class VenueRequestItemInlineAdmin(admin.StackedInline):
    model = VenueRequestItem
    raw_id_fields = ('venue', 'foirequest', 'publicbody',)


class VenueRequestAdmin(admin.ModelAdmin):
    inlines = [
        VenueRequestItemInlineAdmin
    ]


admin.site.register(VenueRequest, VenueRequestAdmin)

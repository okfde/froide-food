from django.contrib import admin

from .models import VenueRequest


class VenueRequestAdmin(admin.ModelAdmin):
    raw_id_fields = ('foirequest', 'publicbody')


admin.site.register(VenueRequest, VenueRequestAdmin)

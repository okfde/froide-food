from django.contrib import admin

from .models import VenueRequest


class VenueRequestAdmin(admin.ModelAdmin):
    pass


admin.site.register(VenueRequest, VenueRequestAdmin)

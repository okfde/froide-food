from datetime import timedelta

from django.contrib import admin
from django.conf.urls import url
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from leaflet.admin import LeafletGeoAdmin

from froide.foirequest.models import FoiRequest
from froide.helper.admin_utils import make_nullfilter
from froide.helper.csv_utils import export_csv_response
from froide.account.models import User

from .models import VenueRequest, VenueRequestItem, FoodSafetyReport


class VenueRequestItemInlineAdmin(admin.StackedInline):
    model = VenueRequestItem
    raw_id_fields = ('venue', 'foirequest', 'publicbody',)


class VenueRequestAdmin(LeafletGeoAdmin):
    display_raw = True
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
    actions = ['merge_venues']

    def get_urls(self):
        urls = super(VenueRequestAdmin, self).get_urls()
        my_urls = [
            url(r'^export-users/$',
                self.admin_site.admin_view(self.export_users),
                name='froide_food-admin-export_users'),
        ]
        return my_urls + urls

    def export_users(self, request):
        if not request.method == 'GET':
            raise PermissionDenied
        if not request.user.is_superuser:
            raise PermissionDenied
        fr_ids = set(
            VenueRequestItem.objects
            .filter(timestamp__year__gte=2019)
            .values_list('foirequest_id', flat=True)
        )
        # -first_message, so last value overwrites user_id
        first_req_timestamp = dict(
            FoiRequest.objects
            .filter(id__in=fr_ids)
            .order_by('-first_message')
            .values_list('user_id', 'first_message')
        )

        queryset = User.objects.filter(
            id__in=list(first_req_timestamp.keys()),
            is_active=True,
            date_joined__year__gte=2019,
        )

        def generator(queryset):
            for u in queryset:
                f = u.foirequest_set.all().order_by('first_message')[0]

                if f.id not in fr_ids:
                    continue
                diff = abs((first_req_timestamp[u.id] - u.date_joined).seconds)
                if diff < 2:
                    yield u

        fields = (
            'id', "first_name", "last_name", "email", 'date_joined'
        )
        stream = User.export_csv(generator(queryset), fields=fields)
        return export_csv_response(stream)

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

    def merge_venues(self, request, queryset):
        """
        Set articles selected as published.
        """
        from .utils import merge_venues
        merge_venues(queryset)

    merge_venues.short_description = 'Merge venues'


class VenueRequestItemAdmin(admin.ModelAdmin):
    list_display = ('venue', 'timestamp',)
    list_filter = ('foirequest__status',)
    date_hierarchy = 'timestamp'

    actions = ['remove_unconfirmed']

    def get_querset(self, request):
        return super().get_querset().prefetch_related(
            'venue', 'foirequest'
        )

    def remove_unconfirmed(self, request, queryset):
        week_ago = timezone.now() - timedelta(days=7)
        queryset = queryset.filter(
            timestamp__lt=week_ago,
            foirequest__status='awaiting_user_confirmation'
        )
        for vri in queryset:
            venue = vri.venue
            vri.delete()
            venue.update_from_items()
    remove_unconfirmed.short_description = 'Alte unbestaetigte entfernen'


class FoodSafetyReportAdmin(admin.ModelAdmin):
    raw_id_fields = (
        'venue', 'request_item',
        'message', 'attachment', 'amenity',
    )


admin.site.register(VenueRequest, VenueRequestAdmin)
admin.site.register(VenueRequestItem, VenueRequestItemAdmin)
admin.site.register(FoodSafetyReport, FoodSafetyReportAdmin)

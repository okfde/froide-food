from datetime import timedelta

from django.contrib import admin
from django.conf.urls import url
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from leaflet.admin import LeafletGeoAdmin

from froide.foirequest.models import FoiRequest
from froide.helper.admin_utils import make_nullfilter
from froide.helper.csv_utils import export_csv_response
from froide.account.models import User, UserTag

from .models import (
    VenueRequest,
    VenueRequestItem,
    FoodSafetyReport,
    FoodAuthorityStatus,
)


class VenueRequestItemInlineAdmin(admin.StackedInline):
    model = VenueRequestItem
    raw_id_fields = (
        "venue",
        "foirequest",
        "publicbody",
    )


class VenueRequestAdmin(LeafletGeoAdmin):
    display_raw = True
    raw_id_fields = ("amenity",)
    inlines = [VenueRequestItemInlineAdmin]
    date_hierarchy = "last_request"
    list_filter = (
        "last_status",
        "last_resolution",
        make_nullfilter("last_request", "Hat Anfrage"),
        make_nullfilter("geo", "Hat eigene Koordinate"),
        make_nullfilter("amenity", "Hat OSM-Betrieb"),
        "amenity__category",
    )
    list_display = (
        "name",
        "last_request",
        "get_last_status_display",
        "get_last_resolution_display",
        "get_provider",
    )
    search_fields = ("name", "ident")
    actions = ["merge_venues"]

    def get_urls(self):
        urls = super(VenueRequestAdmin, self).get_urls()
        my_urls = [
            url(
                r"^export-users/$",
                self.admin_site.admin_view(self.export_users),
                name="froide_food-admin-export_users",
            ),
        ]
        return my_urls + urls

    def export_users(self, request):
        if not request.method == "GET":
            raise PermissionDenied
        if not request.user.is_superuser:
            raise PermissionDenied
        four_months_ago = timezone.now() - timedelta(days=4 * 31)

        queryset = User.objects.filter(
            is_active=True,
            tags__in=UserTag.objects.filter(slug="food-first"),
            date_joined__gte=four_months_ago,
        )

        fields = ("id", "first_name", "last_name", "email", "date_joined")
        stream = User.export_csv(queryset, fields=fields)
        return export_csv_response(stream)

    def get_last_status_display(self, obj):
        return FoiRequest.STATUS_RESOLUTION_DICT.get(
            obj.last_status, (obj.last_status,)
        )[0]

    get_last_status_display.short_description = "letzter Status"

    def get_provider(self, obj):
        return obj.ident.split(":")[0]

    get_provider.short_description = "provider"

    def get_last_resolution_display(self, obj):
        return FoiRequest.STATUS_RESOLUTION_DICT.get(
            obj.last_resolution, (obj.last_resolution,)
        )[0]

    get_last_resolution_display.short_description = "letztes Ergebnis"

    def merge_venues(self, request, queryset):
        """
        Set articles selected as published.
        """
        from .utils import merge_venues

        merge_venues(queryset)

    def save_model(self, request, obj, form, change):
        from .utils import check_and_merge_venue

        if not obj.ident.startswith("amenity:") and obj.amenity:
            # Setting amenity on venue request
            obj.ident = "amenity:%s" % obj.amenity.ident
            obj.update_from_provider()
            check_and_merge_venue(obj)
        super().save_model(request, obj, form, change)

    merge_venues.short_description = "Merge venues"


class VenueRequestItemAdmin(admin.ModelAdmin):
    list_display = (
        "venue",
        "timestamp",
    )
    list_filter = (
        "foirequest__status",
        "foirequest__resolution",
        make_nullfilter("checked_date", "Wurde geprüft"),
    )
    date_hierarchy = "timestamp"
    raw_id_fields = ("venue", "foirequest", "publicbody")

    actions = ["remove_unconfirmed"]

    def get_querset(self, request):
        return super().get_querset().prefetch_related("venue", "foirequest")

    def remove_unconfirmed(self, request, queryset):
        week_ago = timezone.now() - timedelta(days=7)
        queryset = queryset.filter(
            timestamp__lt=week_ago, foirequest__status="awaiting_user_confirmation"
        )
        for vri in queryset:
            venue = vri.venue
            vri.delete()
            venue.update_from_items()

    remove_unconfirmed.short_description = "Alte unbestaetigte entfernen"


class FoodSafetyReportAdmin(admin.ModelAdmin):
    change_list_template = "admin/froide_food/foodsafetyreport/change_list.html"

    raw_id_fields = (
        "venue",
        "request_item",
        "message",
        "attachment",
        "amenity",
    )
    list_display = (
        "venue",
        "date",
        "complaints",
    )
    date_hierarchy = "date"

    list_filter = (
        "complaints",
        "disgusting",
        make_nullfilter("attachment", "Hat Anhang"),
    )

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        response.context_data["distinct_venues"] = (
            qs.distinct("venue").order_by("venue").count()
        )
        return response


class FoodAuthorityStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ("publicbodies",)
    list_display = (
        "title",
        "cooperative",
    )


admin.site.register(VenueRequest, VenueRequestAdmin)
admin.site.register(VenueRequestItem, VenueRequestItemAdmin)
admin.site.register(FoodSafetyReport, FoodSafetyReportAdmin)
admin.site.register(FoodAuthorityStatus, FoodAuthorityStatusAdmin)

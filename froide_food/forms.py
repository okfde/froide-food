from django import forms
from django.utils import timezone

from froide.foirequest.models import FoiAttachment, FoiMessage, FoiRequest

from .models import FoodSafetyReport, VenueRequestItem


class ReportForm(forms.Form):
    reportdate = forms.DateField(required=False)
    unresolved = forms.BooleanField(required=False)
    complaints = forms.BooleanField(required=False)
    disgusting = forms.BooleanField(required=False)
    attachment = forms.ModelChoiceField(
        required=False, queryset=FoiAttachment.objects.all()
    )
    message = forms.ModelChoiceField(required=False, queryset=FoiMessage.objects.all())
    foirequest = forms.ModelChoiceField(queryset=FoiRequest.objects.all())

    def save(self):
        data = self.cleaned_data
        try:
            request_item = VenueRequestItem.objects.get(foirequest=data["foirequest"])
        except VenueRequestItem.DoesNotExist:
            return

        if not data["unresolved"]:
            self.save_report(request_item, data)
        else:
            FoiRequest.objects.filter(id=data["foirequest"].id).update(resolution="")

        VenueRequestItem.objects.filter(id=request_item.id).update(
            checked_date=timezone.now()
        )

    def save_report(self, request_item, data):

        venue = request_item.venue
        amenity = None
        provider_name = venue.get_provider()
        if provider_name == "amenity":
            provider = venue.get_venue_provider()
            amenity = provider.get_object(venue.ident)

        report, created = FoodSafetyReport.objects.update_or_create(
            request_item=request_item,
            venue=venue,
            date=data["reportdate"],
            defaults={
                "message": data["message"],
                "attachment": data["attachment"],
                "amenity": amenity,
                "complaints": data["complaints"],
                "disgusting": data["disgusting"],
            },
        )

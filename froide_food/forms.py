from datetime import timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from froide.foirequest.models import FoiRequest, FoiMessage, FoiAttachment
from froide.helper.widgets import BootstrapRadioSelect

from .models import VenueRequestItem, FoodSafetyReport

APPEAL_TIME = timedelta(days=40)


class AppealForm(forms.Form):
    request = forms.ModelChoiceField(
        label='Anfrage',
        help_text='Wählen Sie die Anfrage aus',
        queryset=None,
        empty_label=None,
        widget=BootstrapRadioSelect
    )
    date_refusal = forms.DateField(
        required=True,
        label='Datum der Ablehnung',
        help_text='Das Datum auf dem letzten Brief der Behörde',
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": _('mm/dd/YYYY')
        }),
        localize=True
    )
    reference = forms.CharField(
        max_length=30,
        required=False,
        label='Geschäftszeichen der Behörde',
        help_text='Das Geschäftszeichen der Behörde auf dem Brief',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    address = forms.CharField(
        max_length=300,
        required=True,
        label='Ihre vollständige Anschrift',
        help_text=(
            'Geben Sie Ihre vollständige Anschrift '
            'mit Name, Adresse, PLZ und Ort ein'
        ),
        widget=forms.Textarea(attrs={
            'rows': '4',
            'class': 'form-control',
            'placeholder': 'Anschrift eingeben'
        })
    )

    def __init__(self, user, foirequests, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['address'].initial = '{name}\n{address}'.format(
            name=user.get_full_name(),
            address=user.address
        )
        self.fields['request'].queryset = foirequests
        if foirequests.count() > 0:
            self.fields['request'].initial = foirequests[0]

    def clean_date_refusal(self):
        refusal_date = self.cleaned_data['date_refusal']

        if refusal_date + APPEAL_TIME < timezone.now().date():
            raise forms.ValidationError(
                'Leider ist die Frist von einem Monat für den '
                'Widerspruch abgelaufen.'
            )
        return refusal_date


class ReportForm(forms.Form):
    reportdate = forms.DateField(required=False)
    unresolved = forms.BooleanField(required=False)
    complaints = forms.BooleanField(required=False)
    attachment = forms.ModelChoiceField(
        required=False,
        queryset=FoiAttachment.objects.all()
    )
    message = forms.ModelChoiceField(
        required=False,
        queryset=FoiMessage.objects.all()
    )
    foirequest = forms.ModelChoiceField(
        queryset=FoiRequest.objects.all()
    )

    def save(self):
        data = self.cleaned_data
        try:
            request_item = VenueRequestItem.objects.get(
                foirequest=data['foirequest']
            )
        except VenueRequestItem.DoesNotExist:
            return

        if not data['unresolved']:
            self.save_report(request_item, data)
        else:
            FoiRequest.objects.filter(id=data['foirequest'].id).update(
                resolution=''
            )

        VenueRequestItem.objects.filter(id=request_item.id).update(
            checked_date=timezone.now()
        )

    def save_report(self, request_item, data):

        venue = request_item.venue
        amenity = None
        provider_name = venue.get_provider()
        if provider_name == 'amenity':
            provider = venue.get_venue_provider()
            amenity = provider.get_object(venue.ident)

        report, created = FoodSafetyReport.objects.update_or_create(
            request_item=request_item,
            venue=venue,
            date=data['reportdate'],
            defaults={
                'message': data['message'],
                'attachment': data['attachment'],
                'amenity': amenity,
                'complaints': data['complaints']
            }
        )
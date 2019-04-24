from datetime import timedelta

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from froide.helper.widgets import BootstrapRadioSelect

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

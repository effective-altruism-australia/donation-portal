import arrow
import os

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import ChoiceInput
from django.conf import settings

from .models import TransitionalDonationsFile, Pledge, PartnerCharity


class TransitionalDonationsFileUploadForm(forms.ModelForm):
    class Meta:
        model = TransitionalDonationsFile
        fields = ['file', ]


class DateRangeSelector(forms.Form):
    def __init__(self, *args, **kwargs):
        last_month = kwargs.pop('last_month', False)
        super(DateRangeSelector, self).__init__(*args, **kwargs)

        years = range(2016, arrow.now().year + 1)
        if last_month:
            start_date = arrow.now().replace(months=-1).replace(day=1).date()
            end_date = arrow.now().replace(day=1).replace(days=-1).date()
        else:
            start_date = arrow.Arrow(2016, 1, 1).date()
            end_date = arrow.now().date()
        self.fields['start'].widget.years = years
        self.fields['start'].initial = start_date
        self.fields['end'].widget.years = years
        self.fields['end'].initial = end_date

    start = forms.DateField(widget=SelectDateWidget(), label='Start date')
    end = forms.DateField(widget=SelectDateWidget(), label='End date')


class PledgeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PledgeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Pledge
        fields = ['amount', 'first_name', 'last_name', 'email', 'subscribe_to_updates',
                  'how_did_you_hear_about_us', 'payment_method', 'recipient_org', 'recurring']

    class Media:
        js = ('js/pledge.js', 'js/process_steps.js', 'js/credit_card.js')
        css = {'all': ('css/pledge.css', 'css/process_steps.css', 'css/credit_card.css',)}

    # These values control the donation amount buttons shown
    donation_amounts = (('$100', 100),
                        ('$250', 250),
                        ('$500', 500),
                        ('$1000', 1000),
                        )

    # The template will display labels for these fields
    show_labels = ['amount', 'how_did_you_hear_about_us']

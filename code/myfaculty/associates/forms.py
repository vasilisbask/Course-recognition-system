from django import forms
from myprofile.models import Associate
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field, HTML
from crispy_forms.helper import FormHelper

EXPORT_LAYOUT = Layout(
            Row(
               Div(HTML('<h3> Επιλέξτε παραμέτρους </h3>'),css_class = 'col-md-4'),
               Div(Submit('submit', 'Εξαγωγή'),css_class='col-md-4 text-end'),
               css_class="row"),
            Row(
                Div(Field('associate'),css_class = 'col-md-4'),
                Div(Field('reference_year'),css_class = 'col-md-4'),
                css_class="row")
)

class export_form(forms.Form):

    reference_year = forms.IntegerField(label = 'Έτος αναφοράς', required=False)
    associate = forms.ModelChoiceField(queryset = Associate.objects.all(), label = 'Συνεργάτης', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = EXPORT_LAYOUT
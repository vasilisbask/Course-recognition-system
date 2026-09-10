from .models import Timesheet
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field, HTML
from django.core.exceptions import ValidationError

def sanitize_fields(fields):
    return_fields = []
    for f in fields:
        if f[-1] == '*' or f[-1] == '-':
            return_fields.append(f[:-1])
        else:
            return_fields.append(f)
    return return_fields

FIELDS = ['month', 'year', 'applicant', 'signed', 'unsigned', 'created_date', 'updated_date']

SEC_EDIT_FIELDS = ['month', 'year', 'applicant', 'signed', 'unsigned', 'created_date', 'updated_date-']

SEC_CREATE_FIELDS = ['month', 'year', 'applicant', 'signed', 'unsigned', 'created_date', 'updated_date-']

STAFF_EDIT_FIELDS = ['month', 'year', 'signed-', 'unsigned', 'created_date-']

STAFF_CREATE_FIELDS = ['month', 'year', 'unsigned']

LABELS ={'month': 'Μήνας',
         'year': 'Έτος',
         'applicant': 'Μέλος Διδακτικού Προσωπικού',
         'signed' : 'Υπογεγραμμένο Timesheet (και από τον Κοσμήτορα)',
         'unsigned' : 'Υπογεγραμμένο Timesheet (από το Μέλος Διδακτικού Προσωπικού)',
         'updated_date' : 'Ημερομηνία τελευταίας ενημέρωσης', 
         'created_date' : 'Ημερομηνία δημιουργίας'}

def build_form_layout(fields):
    layout = Layout(Row(Div(HTML('<h4> Στοιχεία Timesheet </h4>'),css_class = 'col-lg-8'),
                        Div(Submit('submit', 'Ενημέρωση'),css_class='col-lg-4 text-end'),
                        css_class="row"))
    
    for field in sanitize_fields(fields):
        layout.append(
            Row(
                Div(Field(field), css_class="row")
            )
        )
    return layout
                       
def adjust_fields(form):
    for f in form.Meta.efields:
        if f[-1] == '*':
            field = f[:-1]
            form.fields[field].required=True
            form.fields[field].disabled=False
            
        elif f[-1] == '-':
            field = f[:-1]
            form.fields[field].required=False
            form.fields[field].disabled=True


class SecCreateForm(ModelForm):

    class Meta:

        model = Timesheet
        fields = sanitize_fields(SEC_CREATE_FIELDS)
        labels = LABELS
        efields = SEC_CREATE_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_form_layout(SEC_CREATE_FIELDS)

class SecUpdateForm(ModelForm):

    class Meta:

        model = Timesheet
        fields = sanitize_fields(SEC_EDIT_FIELDS)
        labels = LABELS
        efields = SEC_EDIT_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_form_layout(SEC_EDIT_FIELDS)

class StaffCreateForm(ModelForm):

    class Meta:

        model = Timesheet
        fields = sanitize_fields(STAFF_CREATE_FIELDS)
        labels = LABELS
        efields = STAFF_CREATE_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_form_layout(STAFF_CREATE_FIELDS)

class StaffUpdateForm(ModelForm):

    class Meta:

        model = Timesheet
        fields = sanitize_fields(STAFF_EDIT_FIELDS)
        labels = LABELS
        efields = STAFF_EDIT_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_form_layout(STAFF_EDIT_FIELDS)
from .models import Leave
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field, HTML
from django.core.exceptions import ValidationError
from core.forms import GenericModelForm

def sanitize_fields(fields):
    return_fields = []
    for f in fields:
        if f[-1] == '*' or f[-1] == '-':
            return_fields.append(f[:-1])
        else:
            return_fields.append(f)
    return return_fields

LEAVE_FIELDS =['is_editable', 'start_date', 'end_date', 'description', 'country', 'city', 'organization', 'funding_required', 'project_title', 'project_acronym', 'project_code', 'travel_expenses', 
               'stay_expenses', 'registration_expenses', 'ga_document', 'applicant', 'updated_date', 'created_date']

SEC_LEAVE_FIELDS =['is_editable', 'start_date', 'end_date', 'description', 'country', 'city', 'organization', 'funding_required', 'project_title', 'project_acronym', 'project_code', 'travel_expenses', 
                   'stay_expenses', 'registration_expenses', 'ga_document', 'applicant', 'updated_date', 'created_date','updated_date-']

STAFF_CREATE_FIELDS =['start_date*', 'end_date*', 'description*', 'country*', 'city*', 'organization', 'funding_required*', 'project_title', 'project_acronym', 'project_code', 'travel_expenses', 
                      'stay_expenses', 'registration_expenses']

STAFF_EDIT_FIELDS =['start_date*', 'end_date*', 'description*', 'country*', 'city*', 'organization', 'funding_required*', 'project_title', 'project_acronym', 'project_code', 'travel_expenses', 
                      'stay_expenses', 'registration_expenses', 'ga_document-']


LEAVE_LABELS ={'start_date' : 'Ημερομηνία έναρξης άδειας', 
               'is_editable' : 'Μπορεί να υποστεί διόρθωση;', 
               'end_date' : 'Ημερομηνία λήξης άδειας', 
               'description' : 'Αιτιολόγηση μετακίνησης' , 
               'country' : 'Χώρα', 
               'city' : 'Πόλη', 
               'organization' : 'Φορέας υποδοχής', 
               'funding_required' : 'Απαιτείται χρηματοδότηση από πόρους του τμήματος;', 
               'project_title' : 'Τίτλος έργου', 
               'project_acronym' : 'Ακρωνύμιο', 
               'project_code' : 'Κωδικός έργου στον ΕΛΚΕ', 
               'travel_expenses' : 'Κόστη εισητηρίων', 
               'stay_expenses' : 'Κόστη μετάβασης', 
               'registration_expenses' : 'Κόστη εγγραφής', 
               'ga_document' : 'Απόφαση', 
               'applicant' : 'Αιτών', 
               'updated_date' : 'Ημερομηνία τελευταίας ενημέρωσης', 
               'created_date' : 'Ημερομηνία δημιουργίας'}

def build_staff_form_layout():
    layout = Layout(Row(Div(HTML('<h4> Στοιχεία Άδειας </h4>'),css_class = 'col-lg-8'),
                        Div(Submit('submit', 'Ενημέρωση'),css_class='col-lg-4 text-end'),
                        css_class="row"),
                     Row(
                        Div(Field('start_date'),css_class = 'col-lg-6'),
                        Div(Field('end_date'),css_class = 'col-lg-6'),
                        css_class="row"),
                    Row(
                        Div(Field('city'),css_class = 'col-lg-6'),
                        Div(Field('country'),css_class = 'col-lg-6'),
                        css_class="row"),
                    Row(
                        Div(Field('description'),css_class = 'col-lg-12'),
                        css_class="row"),
                    Row(Div(HTML('<h6> Στοιχεία Έργου </h6>'),css_class = 'col-lg-8'),
                        css_class="row"),   
                    Row(Div(HTML('<p> Συμπληρώνετε σε περίπτωση που πραγματοποιείται στα πλαίσια κάποιου έργου του ΕΛΚΕ </p>'),css_class = 'col-lg-12'),
                        css_class="row"), 
                    Row(
                        Div(Field('project_title'),css_class = 'col-lg-4'),
                        Div(Field('project_acronym'),css_class = 'col-lg-4'),
                        Div(Field('project_code'),css_class = 'col-lg-4'),
                        css_class="row"),                        
                    Row(Div(HTML('<h6> Χρηματοδότηση </h6>'),css_class = 'col-lg-8'),
                        css_class="row"),   
                    Row(Div(HTML('<p> Συμπληρώνετε σε περίπτωση που θέλετε να χρηματοδοτηθεί από πόρους του Τμήματος </p>'),css_class = 'col-lg-12'),
                        css_class="row"), 
                    Row(
                        Div(Field('travel_expenses'),css_class = 'col-lg-4'),
                        Div(Field('stay_expenses'),css_class = 'col-lg-4'),
                        Div(Field('registration_expenses'),css_class = 'col-lg-4'),
                        css_class="row"), 
                    )
    return layout

def build_sec_form_layout():
    layout = build_staff_form_layout()
    layout.append(Layout(
        Row(
            Div(Field('applicant'),css_class = 'col-lg-12'),
                css_class="row"),
            Row(
            Div(Field('ga_document'),css_class = 'col-lg-12'),
                css_class="row"),
             Row(
            Div(Field('created_date'),css_class = 'col-lg-6'),
            Div(Field('updated_date'),css_class = 'col-lg-6'),
            css_class="row")
        ))    
    return layout

def build_staff_form_edit_layout():
    layout = build_staff_form_layout()
    layout.append(Layout(
        Row(
            Div(Field('ga_document'),css_class = 'col-lg-12'),
                css_class="row")
        ),
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


class SecCreateLeaveForm(GenericModelForm):

    class Meta:

        model = Leave
        fields = sanitize_fields(SEC_LEAVE_FIELDS)
        labels = LEAVE_LABELS
        efields = SEC_LEAVE_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_sec_form_layout()

class SecUpdateLeaveForm(GenericModelForm):

    class Meta:

        model = Leave
        fields = sanitize_fields(SEC_LEAVE_FIELDS)
        labels = LEAVE_LABELS
        efields = SEC_LEAVE_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_sec_form_layout()

class StaffCreateLeaveForm(GenericModelForm):

    class Meta:

        model = Leave
        fields = sanitize_fields(STAFF_CREATE_FIELDS)
        labels = LEAVE_LABELS
        efields = STAFF_CREATE_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_staff_form_layout()
        

class StaffUpdateLeaveForm(GenericModelForm):

    class Meta:

        model = Leave
        fields = sanitize_fields(STAFF_EDIT_FIELDS)
        labels = LEAVE_LABELS
        efields = STAFF_EDIT_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_staff_form_edit_layout()
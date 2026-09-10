from django import forms
from .models import Project
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field, HTML
from django.core.exceptions import ValidationError
from dal import autocomplete


def sanitize_fields(fields):
    return_fields = []
    for f in fields:
        if f[-1] == '*' or f[-1] == '-':
            return_fields.append(f[:-1])
        else:
            return_fields.append(f)
    return return_fields


PROJECT_FIELDS = [ 'title', 'acronym*', 'budget_total', 'budget_dep', 'call', 'thematic_areas', 'approved', 'submission_approved_ga', 'implementation_approved_ga', 
                  'department_role', 'department_staff',  'abstract', 'partners', 'funding_date', 'duration', 'start', 'submission_date', 
                 'document_approved_submission', 'document_approved_implementation', 'coordinator', 'updated_date', 'created_date', 'is_editable']

SEC_CREATE_PROJECT_FIELDS = [ 'title', 'acronym', 'budget_total', 'budget_dep', 'call', 'thematic_areas', 'approved', 'submission_date',
                          'department_role', 'department_staff',  'abstract', 'partners', 'funding_date', 'duration', 'start', 'coordinator']

SEC_UPDATE_PROJECT_FIELDS = [ 'title', 'acronym', 'budget_total', 'budget_dep', 'call', 'thematic_areas', 'approved', 'submission_approved_ga', 'implementation_approved_ga', 
                      'department_role', 'department_staff',  'abstract', 'partners', 'funding_date', 'duration', 'start', 'submission_date', 
                     'document_approved_submission', 'document_approved_implementation', 'coordinator', 'updated_date-', 'created_date-', 'is_editable']

STAFF_CREATE_PROJECT_FIELDS = [ 'title*', 'acronym', 'budget_total*', 'budget_dep*', 'call*', 'thematic_areas*', 'approved*', 
                          'department_role*', 'department_staff*',  'abstract*', 'partners*', 'funding_date*', 'duration*', 'start*', 'submission_date*',]


STAFF_UPDATE_PROJECT_FIELDS = [ 'title*', 'acronym*', 'budget_total*', 'budget_dep*', 'call*', 'thematic_areas*', 'approved*', 'submission_approved_ga-', 'implementation_approved_ga-', 
                      'department_role*', 'department_staff*',  'abstract*', 'partners*', 'funding_date*', 'duration*', 'start*', 'submission_date*', 
                     'document_approved_submission-', 'document_approved_implementation-', 'coordinator-', 'updated_date-', 'created_date-', 'is_editable-']


PROJECT_LABELS= {'is_editable': 'Μπορεί να υποστεί επεξεργασία;', 
                 'approved': 'Το έργο έχει εγκριθεί για χρηματοδότηση;', 
                 'submission_approved_ga': 'Συνέλευση Έγκρισης Υποβολής', 
                 'implementation_approved_ga': 'Συνέλευση Έγκρισης Υποβολής', 
                 'budget_total': 'Π/Υ πρότασης (Ευρώ)', 
                 'budget_dep': 'Π/Υ τμήματος (Ευρώ)' , 
                 'call': 'Πρόσκληση', 
                 'thematic_areas': 'Θεματικές περιοχές', 
                 'title': 'Τίτλος', 
                 'department_role': 'Ρόλος του Τμήματος', 
                 'department_staff': 'Περιγράψτε την ομάδα εργασίας από το Τμήμα', 
                 'acronym': 'Ακρωνύμιο', 
                 'abstract': 'Περίληψη', 
                 'partners': 'Εταίροι', 
                 'funding_date': 'Ποσοστό Χρηματοδότησης', 
                 'duration': 'Διάρκεια (σε μήνες)', 
                 'start': 'Ημερομηνία Έναρξης', 
                 'document_approved_submission': 'Πρακτικό Έγκρισης Υποβολής', 
                 'document_approved_implementation': 'Πρακτικό Έγκρισης Υλοποίησης', 
                 'coordinator': 'Συντονιστής', 
                 'updated_date': 'Τελευταία Ενημέρωση', 
                 'created_date': 'Ημερομηνία Υποβολής Αιτήματος',
                 'submission_date': 'Προθεσμία Υποβολής'
                 }

def append_fields_to_layout(layout, fields):
    for field in sanitize_fields(fields):
        layout.append(
            Row(
                Div(Field(field), css_class="row")
            )
        )
    return layout

def build_form_layout(fields):
    project_layout = Layout(Row(Div(HTML('<h4> Στοιχεία Έργου </h4>'),css_class = 'col-lg-8'),
                        Div(Submit('submit', 'Ενημέρωση'),css_class='col-lg-4 text-end'),
                        css_class="row"))

    project_layout = append_fields_to_layout(project_layout,fields)
    return project_layout

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


class SecCreateProjectForm(ModelForm):

    class Meta:

        model = Project
        fields = sanitize_fields(SEC_CREATE_PROJECT_FIELDS)
        labels = PROJECT_LABELS
        efields = SEC_CREATE_PROJECT_FIELDS
        widgets = {
            "coordinator" : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete'),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_form_layout(self.fields)
        

class SecUpdateProjectForm(ModelForm):

    class Meta:

        model = Project
        fields = sanitize_fields(SEC_UPDATE_PROJECT_FIELDS)
        labels = PROJECT_LABELS
        efields = SEC_UPDATE_PROJECT_FIELDS
        widgets = {
            "coordinator" : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete'),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_form_layout(self.fields)

class StaffCreateProjectForm(ModelForm):

    class Meta:

        model = Project
        fields = sanitize_fields(STAFF_CREATE_PROJECT_FIELDS)
        labels = PROJECT_LABELS
        efields = STAFF_CREATE_PROJECT_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_form_layout(self.fields)

class StaffUpdateProjectForm(ModelForm):

    class Meta:

        model = Project
        fields = sanitize_fields(STAFF_UPDATE_PROJECT_FIELDS)
        labels = PROJECT_LABELS
        efields = STAFF_UPDATE_PROJECT_FIELDS
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adjust_fields(self)
        self.helper = FormHelper()
        self.helper.layout = build_form_layout(self.fields)
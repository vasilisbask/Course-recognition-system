from django import forms
from .models import Call, Application, Degree, ReferenceLetter, JournalPublication, ConferencePublication, WorkExperience, ReferenceContact
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, Field, HTML
from django.core.exceptions import ValidationError
from dal import autocomplete
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models.query import EmptyQuerySet
from crispy_forms.layout import Field
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from scopes.utils import get_secreteriat_scope
from core.forms import GenericModelForm
from datetime import datetime
from myprofile.checks import is_staff_member
from myprofile.models import PersonalInfo
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date

def date_in_future(d):
    now = date.today()
    return d > now

def year_in_future(year):
    this_year = date.today().year
    return year > this_year

LABELS = {

    # =========================
    # Call
    # =========================
    "title": _("Τίτλος"),
    "title_en": _("Τίτλος (Αγγλικά)"),
    "description": _("Περιγραφή"),
    "start": _("Ημερομηνία Έναρξης"),
    "end": _("Ημερομηνία Λήξης"),
    "supervisor": _("Επιβλέπων"),
    "reviewers": _("Αξιολογητές"),
    "invitation_document": _("Έγγραφο Πρόσκλησης"),
    "published": _("Δημοσιευμένη"),
    "program": _("Πρόγραμμα Σπουδών"),
    "deadline": _("Ημερομηνία Λήξης"),
    "from_date" : _("Ημερομηνία Έναρξης"),
    

    # =========================
    # Application
    # =========================
    "cv" : _('Βιογραφικό Σημείωμα'),
    "applicant": _("Υποψήφιος"),
    "call": _("Πρόσκληση"),
    "id_document" : _('Αντίγραφο Ταυτότητας ή Διαβατηρίου'),
    "doctoral_plan": _("Πλάνο Διδακτορικής Διατριβής"),
    "date_submitted": _("Ημερομηνία Υποβολής"),
    "notes": _("Σημειώσεις"),
    "status": _("Κατάσταση"),
    "ref_letters": _("Συστατικές Επιστολές"),
    "declaration_not_enlisted": _("Υπεύθυνη Δήλωση"),
    "additional_doc": _("Επιπλέον Τεκμηρίωση"),
    "rf": _("Αριθμός Αναφοράς Συστήματος"),
    "rf_num":_("Αριθμός Ιδρυματικού Πρωτοκόλλου"),
    "given_name": _("Όνομα"),
    "surname": _("Επώνυμο"),
    "fathers_name": _("Όνομα Πατέρα"),
    "date_of_birth": _("Ημερομηνία Γέννησης"),
    "gender": _("Φύλο"),
    "home_address_street": _("Οδός Κατοικίας"),
    "home_address_no": _("Αριθμός Κατοικίας"),
    "home_address_po_box": _("Ταχυδρομικός Κώδικας Κατοικίας"),
    "home_address_city": _("Πόλη Κατοικίας"),
    "home_address_country": _("Χώρα Κατοικίας"),
    "mobile_phone": _("Κινητό Τηλέφωνο"),
    "home_phone": _("Σταθερό Τηλέφωνο"),
    "work_address_street": _("Οδός Εργασίας"),
    "work_address_no": _("Αριθμός Εργασίας"),
    "work_address_po_box": _("Τ.Κ. Εργασίας"),
    "work_address_city": _("Πόλη Εργασίας"),
    "work_address_country": _("Χώρα Εργασίας"),
    "work_phone": _("Τηλέφωνο Εργασίας"),
    "pic": _("Φωτογραφία"),
    "last_update": _("Τελευταία Ενημέρωση"),

    # =========================
    # Degree
    # =========================
    "type": _("Τύπος Πτυχίου"),
    "university": _("Πανεπιστήμιο"),
    "school": _("Σχολή"),
    "department": _("Τμήμα"),
    "score": _("Βαθμός"),
    "degree": _("Αντίγραφο Πτυχίου"),
    "year": _("Έτος"),
    "transcript_of_records": _("Αναλυτική Βαθμολογία"),

    # =========================
    # ReferenceLetter
    # =========================
    "doctorate_application": _("Αίτηση Διδακτορικού"),
    "email": _("Email"),
    "phone": _("Τηλέφωνο"),
    "letter": _("Συστατική Επιστολή"),
    "surname": _("Επώνυμο"),
    "given_name": _("Όνομα"),
    "title": _("Τίτλος"),
    "institution": _("Ίδρυμα/Φορέας"),
    "submitted_date": _("Ημερομηνία Υποβολής"),
    "contact": _("Στοιχεία Επαφής"),

    # =========================
    # ReferenceContact
    # =========================
    # (επανάληψη applicant/contact fields καλύπτεται ήδη)

    # =========================
    # JournalPublication
    # =========================
    "journal_title": _("Τίτλος Περιοδικού"),
    "authors": _("Συγγραφείς"),
    "publisher": _("Εκδότης"),
    "volume": _("Τόμος"),
    "pages": _("Σελίδες"),
    "link": _("Σύνδεσμος"),
    "doi": _("DOI"),
    "pdf": _("Αρχείο PDF"),

    # =========================
    # ConferencePublication
    # =========================
    "conference_title": _("Τίτλος Συνεδρίου"),

    # =========================
    # WorkExperience
    # =========================
    "company": _("Εταιρεία / Φορέας"),
    "start_date": _("Ημερομηνία Έναρξης"),
    "end_date": _("Ημερομηνία Λήξης"),
    "duties": _("Καθήκοντα"),
    "contract": _("Σύμβαση (ή άλλο αποδεικτικό)"),
}

HELPTEXTS = {
   "doctoral_plan": _("Αρχείο PDF που περιγράφει το πλάνο της διδακτορικής διατριβής, όπως απαιτείται από την πρόσκληση."),
   "cv": _("Βιογραφικό σημείωμα σε μορφή PDF. Δεν υπάρχει κάποιο προτεινόμενο format."),
   "notes" : _('Σημειώσεις που θα θέλατε να ληφθούν υπόψη από την επιτροπή αξιολόγησης. (Προαιρετικό)'),
   "additional_doc" : _('Κάποιο επιπλέον αρχείο PDF με τεκμηρίωση που θα θέλατε να ληφθούν υπόψη από την επιτροπή αξιολόγησης. (Προαιρετικό)'),   
   "declaration_not_enlisted" : _('Υπεύθυνη δήλωση σε μορφή PDF που να δηλώνει ότι δεν είστε εγγεγραμμένος σε κάποιο άλλο διδακτορικό πρόγραμμα.'),   
}

class PhdAppForm(GenericModelForm):

    extra_dict = LABELS
    help_texts = HELPTEXTS

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            user = kwargs['user']
            if user:
                if is_staff_member(user) and not user.is_superuser:        
                    self.disabled = True
                    
        super().__init__(*args, **kwargs)

        for field_name, label in self.extra_dict.items():
            if field_name in self.fields:
                self.fields[field_name].label = label
        
        for field_name, help_text in self.help_texts.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = help_text
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        year = cleaned_data.get('year')
        deadline = cleaned_data.get('deadline')
        from_date = cleaned_data.get('start_date')

        if start_date and end_date:
            if start_date > end_date:
                self.add_error('start_date', _('H ημερομηνία έναρξης δεν μπορεί να είναι προγενέστερη της ημερομηνίας λήξης') )

        if from_date and deadline:
            if from_date > deadline:
                self.add_error('start_date', _('H ημερομηνία έναρξης δεν μπορεί να είναι προγενέστερη της ημερομηνίας λήξης') )

        if start_date:    
            if date_in_future(start_date):
                self.add_error('start_date', _('H ημερομηνία δεν μπορεί να είναι στο μέλλον.') )
            
        if end_date:
            if date_in_future(end_date):
                self.add_error('end_date', _('H ημερομηνία δεν μπορεί να είναι στο μέλλον.') )

        if year:
            if year_in_future(year):
                self.add_error('year', _('Δεν μπορείτε να καταχωρήσετε χρονιά που ανήκει στο μέλλον.') )

        # Make sure only PDFs are uploaded!

        for name, field in self.fields.items():
            if isinstance(field, forms.FileField):
                file = cleaned_data.get(name)

                if file:
                    if not file.name.lower().endswith(".pdf"):
                        self.add_error(name, _('Δεν επιτρέπεται να ανεβάσετε αρχείο που δεν είναι της μορφής PDF.'))
                        continue

                    header = file.read(4)
                    file.seek(0)

                    if header != b"%PDF":
                        self.add_error(name, _('Δεν φαίνεται να ανεβάσατε κατάλληλο PDF αρχείο.'))
        return cleaned_data

class CandidateForm(PhdAppForm):

    def __init__(self, *args, **kwargs):
        # For existing objects make sure the candidate can not edit if the call date has passed
        # or the status is anything else than draft
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance:
                if instance.id:
                    application = instance.application
                    if not application.applicant_can_edit():
                        self.disabled = True
            
        super().__init__(*args, **kwargs)

class ReviewerForm(PhdAppForm):
    disabled = True

SEC_CALL_FIELDS = ['program', 'title', 'title_en', 'description', 'from_date', 'deadline', 'supervisor', 'reviewers', 'invitation_document', 'published']
SEC_CALL_REQUIRED = ['program', 'title', 'title_en', 'from_date', 'deadline', 'supervisor', 'reviewers', 'invitation_document']

class SecCallForm(PhdAppForm):
    required_fields_extra = SEC_CALL_REQUIRED

    class Meta:
        fields = SEC_CALL_FIELDS

        widgets = {
            'reviewers' : autocomplete.ModelSelect2Multiple(url='myprofile:staffmember-autocomplete'),
            'supervisor' : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete')
        }
        model = Call

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        scope = get_secreteriat_scope(self.user)
        self.fields['program'].queryset = scope['programs']

SEC_APPLICATION_FIELDS = ['cv', 'id_document', 'call', 'doctoral_plan', 'date_submitted', 'notes',
                  'status', 'declaration_not_enlisted',
                  'additional_doc', 'rf', 'rf_num']

class SecApplicationForm(PhdAppForm):

    disabled_fields = ['rf', 'date_submitted']

    class Meta:
        model = Application 
        fields = SEC_APPLICATION_FIELDS

class ReviewerApplicationForm(PhdAppForm):
    
    disabled=True
    
    class Meta:
        model = Application 
        fields = SEC_APPLICATION_FIELDS

               
REQUIRED_APPLICATION_FIELDS = ['cv', 'id_document', 'doctoral_plan', 'declaration_not_enlisted']
APPLICATION_FIELDS = ['cv', 'id_document', 'doctoral_plan', 'notes', 'declaration_not_enlisted', 'additional_doc']

class CandidateUpdateApplicationForm(PhdAppForm):
    
    required_fields_extra = REQUIRED_APPLICATION_FIELDS
    
    class Meta:
        model = Application
        fields = APPLICATION_FIELDS

    def __init__(self, *args, **kwargs):
    # For existing objects make sure the candidate can not edit if the call date has passed
    # or the status is anything else than draft
    
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance:
                if instance.id:
                    if not instance.applicant_can_edit():
                        self.disabled = True
            
        super().__init__(*args, **kwargs)


DEGREE_FIELDS = ['year', 'type', 'university', 'school', 'department', 'score', 
                  'degree', 'transcript_of_records']

class SecDegreeForm(PhdAppForm):
        
    class Meta:
        model = Degree
        fields = DEGREE_FIELDS

class CandidateDegreeForm(CandidateForm):

    required_all = True

    class Meta:
        model = Degree
        fields = DEGREE_FIELDS

class ReviewerDegreeForm(PhdAppForm):
    disabled = True

    class Meta:
        model = Degree
        fields = DEGREE_FIELDS

class SecContactForm(PhdAppForm):
        
    class Meta:
        model = ReferenceContact
        fields = ['email', 'phone', 'surname', 'given_name', 
                  'title', 'institution']
        
class CandidateContactForm(PhdAppForm):
    required_all = True

    class Meta:
        model = ReferenceContact
        fields = ['email', 'phone', 'surname', 'given_name', 
                  'title', 'institution']
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance:
            if instance.id:
                application = instance.application
                if (application.status == Application.SUBMITTED) or not application.applicant_can_edit():

                    self.disabled = True
        super().__init__(*args, **kwargs)
        

JOURNAL_FIELDS = ['title', 'journal_title', 'authors', 'publisher', 'volume', 
                  'pages', 'year', 'link', 'doi', 'pdf']

class SecJournalForm(PhdAppForm):
    class Meta:
        model = JournalPublication
        fields = JOURNAL_FIELDS

class CandidateJournalForm(CandidateForm):
    class Meta:
        model = JournalPublication
        fields = JOURNAL_FIELDS

class ReviewerJournalForm(PhdAppForm):
    disabled = True

    class Meta:
        model = JournalPublication
        fields = JOURNAL_FIELDS

CONFERENCE_FIELDS = ['title', 'conference_title', 'authors', 'year', 'link', 'doi', 'pdf']
class SecConferenceForm(PhdAppForm):
        
    class Meta:
        model = ConferencePublication
        fields = CONFERENCE_FIELDS

class ReviewerConferenceForm(PhdAppForm):
    
    disabled = True

    class Meta:
        model = ConferencePublication
        fields = CONFERENCE_FIELDS

class CandidateConferenceForm(CandidateForm):

    class Meta:
        model = ConferencePublication
        fields = CONFERENCE_FIELDS
        

class ExperienceForm(CandidateForm):
    help_texts = {
        'end_date' : _('Κάντε click στο πεδίο και επιλέξτε. Αν απασχολείστε ακόμα εκεί καταχωρείστε την σημερινή ημερομηνία.')
    }

EXPERIENCE_FIELDS = ['title', 'company', 'start_date', 'end_date', 'duties', 'contract']

class SecExperienceForm(ExperienceForm):
        
    class Meta:
        model = WorkExperience
        fields = EXPERIENCE_FIELDS

class ReviewerExperienceForm(ExperienceForm):

    disabled = True        
    class Meta:
        model = WorkExperience
        fields = EXPERIENCE_FIELDS

class CandidateExperienceForm(ExperienceForm):

    class Meta:
        model = WorkExperience
        fields = EXPERIENCE_FIELDS

PI_FIELDS = ['given_name', 'surname', 'fathers_name', 'date_of_birth', 'gender',
                  'home_address_street','home_address_no', 'home_address_po_box',
                  'home_address_city','home_address_country', 'mobile_phone',
                  'home_phone']

REQUIRED_PI_FIELDS = PI_FIELDS

class CandidatePIFrom(PhdAppForm):

    required_all = True
    class Meta:
        model = PersonalInfo
        fields = REQUIRED_PI_FIELDS

class ReviewerPIFrom(PhdAppForm):
    disabled = True

    class Meta:
        model = PersonalInfo
        fields = PI_FIELDS

class SecPIFrom(PhdAppForm):

    class Meta:
        model = PersonalInfo
        fields = PI_FIELDS


CALL_FIELDS = ['title', 'title_en', 'description', 'from_date', 'deadline', 'supervisor', 'reviewers', 'invitation_document']
CANDIDATE_CALL_FIELDS = ['title', 'title_en', 'description', 'from_date', 'deadline', 'supervisor', 'invitation_document']

class DisabledCallForm(PhdAppForm):
    disabled = True
    class Meta:
        model = Call
        fields = CANDIDATE_CALL_FIELDS
        
class ReferenceLetterForm(GenericModelForm):

    submit_button_text = _('Υποβολή Συστατικής Επιστολής')
 
    class Meta:
        model = ReferenceLetter
        fields = ['letter', 'surname', 'given_name', 'email', 'institution', 'title',  'phone', 'notes']
        labels = LABELS

class ReviewerLetterForm(ReferenceLetterForm):
    disabled = True
    

class SecLetterForm(ReferenceLetterForm):
    pass
######################################################################
# Reviewer Forms
######################################################################







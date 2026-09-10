from django import forms
from django.utils.translation import gettext_lazy as _
from core.forms import GenericModelForm
from .models import PhdThesis, ThesisProgress, Recommendation, JournalPublication, ConferencePublication, TaskModel, TeachingTask, AdministrativeTask
from dal import autocomplete
from myprofile.models import Student, PersonalInfo, StaffMember
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.core.exceptions import ValidationError

FIELD_LABELS = {
    # Student
    'email' : _('Email'), 
    'given_name' : _('Όνομα'), 
    'surname' : _('Επώνυμο'), 
    'program' : _('Πρόγραμμα Σπουδών'),
    'reg_num' : _('Αριθμός μητρώου'),

    # PhdThesis
    "candidate": _("Υποψήφιος Διδάκτορας"),
    "supervisor": _("Επιβλέπων Καθηγητής"),
    "committee": _("Τριμελής Συμβουλευτική Επιτροπή"),
    "subject_gr": _("Τίτλος Διατριβής (Ελληνικά)"),
    "subject_en": _("Τίτλος Διατριβής (Αγγλικά)"),
    "inscription_date": _("Ημερομηνία Εγγραφής"),
    "inscription_year": _("Έτος Εγγραφής"),
    "inscription_ga": _("Αριθμός Πράξης Εγγραφής"),
    "graduation_date": _("Ημερομηνία Αναγόρευσης"),
    "graduation_ga": _("Συνέλευση Αναγόρευσης"),    
    "status" : _("Κατάσταση Φοίτησης"),
    "notes": _("Σημειώσεις"),
    "abstract_gr": _("Περίληψη (Ελληνικά)"),
    "abstract_en": _("Περίληψη (Αγγλικά)"),

    # ThesisScopedModel
    "thesis": _("Διδακτορική Διατριβή"),

    # JournalPublication
    "title": _("Τίτλος"),
    "journal_title": _("Τίτλος Περιοδικού"),
    "authors": _("Συγγραφείς"),
    "publisher": _("Εκδότης"),
    "volume": _("Τόμος"),
    "pages": _("Σελίδες"),
    "year": _("Έτος"),
    "link": _("Σύνδεσμος"),
    "doi": _("DOI"),
    "pdf": _("Αρχείο PDF"),
    "has_supervisor" : _('Συμμετέχει στη δημοσίευση ο επιβλέπων καθηγητής;'),
    "issue" : _('Τεύχος'),

    # ConferencePublication
    "conference_title": _("Τίτλος Συνεδρίου"),

    # TaskModel
    "faculty": _("Μέλος ΔΕΠ"),

    # TeachingTask
    "course": _("Μάθημα"),
    "hours_per_week": _("Ώρες ανά Εβδομάδα"),
    "no_weeks": _("Αριθμός Εβδομάδων"),
    "under_contract": _("Με Σύμβαση"),
    "start_date": _("Ημερομηνία Έναρξης"),
    "end_date": _("Ημερομηνία Λήξης"),

    # ExamSupervision
    "exam_date": _("Ημερομηνία Εξέτασης"),

    # AdministrativeTask
    "total_hours": _("Συνολικές Ώρες Απασχόλησης"),

    # ThesisProgress
    "rfs": _("Σχετική Απόφαση / Έγγραφο"),
    "created_at": _("Ημερομηνία Δημιουργίας"),
    "updated_at": _("Ημερομηνία Τελευταίας Ενημέρωσης"),
    "created_by": _("Χρήστης που Δημιούργησε την Εγγραφή"),
    "updated_by": _("Χρήστης που Ενημέρωσε Τελευταίος την Εγγραφή"),    
    
    "decision_date": _("Ημερομηνία Απόφασης"),

    # Recommendation
    "recommendation" :  _('Εισήγηση'),
    "recommender" :  _('Επιβλέπων'),
    "supporting_document" : _('Επισυναπτόμενο έγγραφο'),
    
    # Personal Info
    "user": _("Χρήστης"),
    "department": _("Τμήμα"),
    "program": _("Πρόγραμμα Σπουδών"),

    "email": _("Ηλεκτρονική Διεύθυνση"),
    "secondary_email": _("Δευτερεύουσα Ηλεκτρονική Διεύθυνση"),
    "fathers_name": _("Όνομα Πατέρα"),
    "date_of_birth": _("Ημερομηνία Γέννησης"),
    "tin": _("Αριθμός Φορολογικού Μητρώου (ΑΦΜ)"),
    "ssn": _("Αριθμός Μητρώου Κοινωνικής Ασφάλισης (ΑΜΚΑ)"),
    "gender": _("Φύλο"),

    "home_address_street": _("Οδός Κατοικίας"),
    "home_address_no": _("Αριθμός Κατοικίας"),
    "home_address_po_box": _("Ταχυδρομικός Κώδικας Κατοικίας"),
    "home_address_city": _("Πόλη Κατοικίας"),
    "home_address_country": _("Χώρα Κατοικίας"),
    "mobile_phone": _("Κινητό Τηλέφωνο"),
    "home_phone": _("Τηλέφωνο Κατοικίας"),

    "work_address_street": _("Οδός Εργασίας"),
    "work_address_no": _("Αριθμός Εργασίας"),
    "work_address_po_box": _("Ταχυδρομικός Κώδικας Εργασίας"),
    "work_address_city": _("Πόλη Εργασίας"),
    "work_address_country": _("Χώρα Εργασίας"),
    "work_phone": _("Τηλέφωνο Εργασίας"),

    "pic": _("Φωτογραφία"),
    "last_update": _("Τελευταία Ενημέρωση"),
}

"""
Secretariat Forms
"""

class SecThesisForm(GenericModelForm):

    scoped_fields = ['candidate', 'supervisor']
    
    class Meta:
        fields = ['candidate', 'supervisor', 'committee', 'status',
                  'subject_gr', 'subject_en', 'inscription_date',
                  'inscription_ga', 'abstract_gr', 'abstract_en', 
                  'graduation_date', 'graduation_ga', 'notes']
        model = PhdThesis
        labels = FIELD_LABELS
        widgets = {
            'candidate' : autocomplete.ModelSelect2(url='myprofile:phd-student-autocomplete'),
            'committee' : autocomplete.ModelSelect2Multiple(url='myprofile:staffmember-autocomplete'),
            'supervisor' : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete')
        }

class SecStudentForm(GenericModelForm):

    scoped_fields = ['program']

    class Meta:
        fields = ['email', 'given_name', 'surname', 'program', 'reg_num']
        labels = FIELD_LABELS
        model = Student

class SecPersonalInfoForm(GenericModelForm):

    scoped_fields = ['department', 'program']
    disabled_fields = ['email']

    class Meta:
        fields = ['email', 'secondary_email', 'fathers_name',
                  'date_of_birth', 'gender',                  
                  'home_address_street', 'home_address_no', 'home_address_po_box',
                  'home_address_city', 'home_address_country',
                  'mobile_phone', 'home_phone']
        
        model = PersonalInfo
        labels = FIELD_LABELS


class SecThesisReportForm(GenericModelForm):

    class Meta:
        fields = ['thesis', 'pdf', 'year', 'notes']
        model = ThesisProgress
        widgets = {
            'thesis' : autocomplete.ModelSelect2(url='phdstuds:sec-phd-thesis-autocomplete'),
        }
        labels = FIELD_LABELS

class SecRecommendationForm(GenericModelForm):

    class Meta:
        fields = ['thesis', 'year', 'notes', 'recommendation', 'recommender', 'supporting_document']
        model = Recommendation
        widgets = {
            'recommender' : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete'),
            'thesis' : autocomplete.ModelSelect2(url='phdstuds:sec-phd-thesis-autocomplete'),
        }
        labels = FIELD_LABELS

class SecJournalForm(GenericModelForm):

    class Meta:
        fields = ['thesis', 'year', 'has_supervisor', 'title',
                  'journal_title', 'publisher', 'issue', 
                  'volume', 'pages', 'doi', 'link', 'pdf']
        model = JournalPublication
        widgets = {
            'thesis' : autocomplete.ModelSelect2(url='phdstuds:sec-phd-thesis-autocomplete'),
        }
        labels = FIELD_LABELS

class SecConferenceForm(GenericModelForm):

    class Meta:
        fields = ['thesis', 'year', 'has_supervisor', 'title',
                  'conference_title', 'venue', 
                  'doi', 'link', 'pdf']
        model = ConferencePublication
        widgets = {
            'thesis' : autocomplete.ModelSelect2(url='phdstuds:sec-phd-thesis-autocomplete'),
        }
        labels = FIELD_LABELS

class SecTeachingTaskForm(GenericModelForm):

    class Meta:
        fields = ['course', 'course_name', 'hours_per_week',
                  'no_weeks', 'year', 'under_contract', 'start_date',
                  'end_date', 'faculty', 'notes']
        widgets = {
            'faculty' : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete'),
        }
        model = TeachingTask
        labels = FIELD_LABELS

class SecAdministrativeTaskForm(GenericModelForm):

    class Meta:
        fields = ['title', 'start_date',
                  'end_date', 'total_hours', 
                  'faculty', 'notes']
        widgets = {
            'faculty' : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete'),
        }
        model = AdministrativeTask
        labels = FIELD_LABELS

"""
Staff Forms
"""
class StaffThesisForm(GenericModelForm):

    disabled = True

    class Meta:
        fields = ['candidate', 'supervisor', 'committee', 'status',
                  'subject_gr', 'subject_en', 'inscription_date',
                  'inscription_ga', 'abstract_gr', 'abstract_en', 
                  'graduation_date', 'graduation_ga', 'notes']
        model = PhdThesis
        labels = FIELD_LABELS
        widgets = {
            'candidate' : autocomplete.ModelSelect2(url='myprofile:phd-student-autocomplete'),
            'committee' : autocomplete.ModelSelect2Multiple(url='myprofile:staffmember-autocomplete'),
            'supervisor' : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete')
        }

class StaffStudentForm(GenericModelForm):

    disabled = True    
    class Meta:
        fields = ['email', 'given_name', 'surname', 'program', 'reg_num']
        labels = FIELD_LABELS
        model = Student

class StaffPersonalInfoForm(GenericModelForm):
    disabled = True
    class Meta:
        fields = ['email', 'secondary_email', 'fathers_name',
                  'date_of_birth', 'gender',                  
                  'home_address_street', 'home_address_no', 'home_address_po_box',
                  'home_address_city', 'home_address_country',
                  'mobile_phone', 'home_phone']
        
        model = PersonalInfo
        labels = FIELD_LABELS

class StaffReportForm(GenericModelForm):
    disabled = True
    class Meta:
        fields = ['thesis', 'pdf', 'year', 'notes']
        model = ThesisProgress
        widgets = {
            'thesis' : autocomplete.ModelSelect2(url='phdstuds:sec-phd-thesis-autocomplete'),
        }
        labels = FIELD_LABELS

class StaffRecommendationForm(GenericModelForm):
    disabled = True        
    class Meta:
        fields = ['thesis', 'year', 'notes', 'recommendation', 'supporting_document']
        model = Recommendation
        widgets = {
            'thesis' : autocomplete.ModelSelect2(url='phdstuds:sec-phd-thesis-autocomplete'),
        }
        labels = FIELD_LABELS

class StaffCreateRecommendationForm(GenericModelForm):

    class Meta:
        fields = ['thesis', 'year', 'notes', 'recommendation', 'supporting_document']
        model = Recommendation        
        labels = FIELD_LABELS
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        staff_member = get_object_or_404(StaffMember, user=self.user)
        self.fields['thesis'].queryset = PhdThesis.objects.filter(supervisor=staff_member)

    def clean_year(self):
        year_now = datetime.now().year
        year = self.cleaned_data['year']
        if year > year_now:
            raise ValidationError(_('Δεν μπορείτε να καταχωρήσετε εισήγηση για επόμενη χρονιά.'))
        return year
        
    def clean(self):
        cleaned_data = super().clean()
        thesis = cleaned_data.get('thesis')
        year = cleaned_data.get('year')
        if thesis and year:
            if Recommendation.objects.filter(thesis=thesis, year=year).exists():
                raise ValidationError(_('Έχετε ήδη καταχωρήσει εισήγηση σε αυτή την χρονιά για αυτήν τη διατριβή.'))
        
        return cleaned_data
    
class StaffJournalForm(GenericModelForm):
    disabled = True
    class Meta:
        fields = ['thesis', 'year', 'has_supervisor', 'title',
                  'journal_title', 'publisher', 'issue', 
                  'volume', 'pages', 'doi', 'link', 'pdf']
        model = JournalPublication
        widgets = {
            'thesis' : autocomplete.ModelSelect2(url='phdstuds:sec-phd-thesis-autocomplete'),
        }
        labels = FIELD_LABELS

class StaffConferenceForm(GenericModelForm):

    disabled = True
    class Meta:
        fields = ['thesis', 'year', 'has_supervisor', 'title',
                  'conference_title', 'venue', 
                  'doi', 'link', 'pdf']
        model = ConferencePublication
        widgets = {
            'thesis' : autocomplete.ModelSelect2(url='phdstuds:sec-phd-thesis-autocomplete'),
        }
        labels = FIELD_LABELS

class StaffTeachingTaskForm(GenericModelForm):
    disabled = True
    class Meta:
        fields = ['course', 'course_name', 'hours_per_week',
                  'no_weeks', 'year', 'under_contract', 'start_date',
                  'end_date', 'faculty', 'notes']
        widgets = {
            'faculty' : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete'),
        }
        model = TeachingTask
        labels = FIELD_LABELS

"""
Staff Forms
"""
class StudentThesisForm(GenericModelForm):

    disabled_fields = ['supervisor', 'committee', 'status',
                  'subject_gr', 'subject_en', 'inscription_date',
                  'inscription_ga']
    class Meta:
        fields = ['supervisor', 'committee', 'status',
                  'subject_gr', 'subject_en', 'inscription_date',
                  'inscription_ga', 'abstract_gr', 'abstract_en' ]
        
        model = PhdThesis
        labels = FIELD_LABELS
        

class StudentStudentForm(GenericModelForm):

    disabled = True    
    class Meta:
        fields = ['email', 'given_name', 'surname', 'program', 'reg_num']
        labels = FIELD_LABELS
        model = Student

class StudentPersonalInfoForm(GenericModelForm):
    disabled_fields = ['email', 'fathers_name', 'date_of_birth', 'gender']

    class Meta:
        fields = ['email', 'secondary_email', 'fathers_name',
                  'date_of_birth', 'gender',                  
                  'home_address_street', 'home_address_no', 'home_address_po_box',
                  'home_address_city', 'home_address_country',
                  'mobile_phone', 'home_phone']
        
        model = PersonalInfo
        labels = FIELD_LABELS

class GenericStudentReportForm(GenericModelForm):
    disabled_fields = ['thesis']

    class Meta:
        fields = ['thesis', 'pdf', 'year', 'notes']
        model = ThesisProgress
        labels = FIELD_LABELS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        student = get_object_or_404(Student, user=self.user)
        thesis = get_object_or_404(PhdThesis, candidate=student)
        self.fields['thesis'].initial = thesis
    
    def clean_year(self):
        year_now = datetime.now().year
        year = self.cleaned_data['year']
        if year > year_now:
            raise ValidationError(_('Δεν μπορείτε να καταχωρήσετε αναφορά για επόμενη χρονιά.'))
        return year
    
    def clean(self):
        cleaned_data = super().clean()
        thesis = cleaned_data.get('thesis')
        year = cleaned_data.get('year')
        if thesis and year:
            if ThesisProgress.objects.filter(thesis=thesis, year=year).exists():
                raise ValidationError(_('Έχετε ήδη καταχωρήσει αναφορά για την χρονιά αυτή'))
        
        return cleaned_data

class StudentUpdateReportForm(GenericStudentReportForm):
    disabled = True


class StudentCreateReportForm(GenericStudentReportForm):
    disabled = False
    
class StudentRecommendationForm(GenericModelForm):
    disabled = True        
    class Meta:
        fields = ['thesis', 'year', 'notes', 'recommendation', 'supporting_document']
        model = Recommendation
        labels = FIELD_LABELS
    
class StudentJournalForm(GenericModelForm):

    required_fields = ['year', 'has_supervisor', 'title',
                      'journal_title', 'publisher', 'issue', 
                      'volume', 'pages', 'doi', 'link']        

    class Meta:
        fields = ['year', 'has_supervisor', 'title',
                  'journal_title', 'publisher', 'issue', 
                  'volume', 'pages', 'doi', 'link', 'pdf']        
        model = JournalPublication        
        labels = FIELD_LABELS

class StudentConferenceForm(GenericModelForm):

    required_fields = ['year', 'has_supervisor', 'title',
                       'conference_title', 'venue', 
                       'doi', 'link']

    class Meta:
        fields = ['year', 'has_supervisor', 'title',
                  'conference_title', 'venue', 
                  'doi', 'link', 'pdf']
        model = ConferencePublication        
        labels = FIELD_LABELS

class StudentTeachingTaskForm(GenericModelForm):
    
    required_fields = ['course_name', 'hours_per_week',
                        'no_weeks', 'year', 'under_contract', 'start_date',
                        'end_date', 'faculty']
    
    class Meta:
        fields = ['course_name', 'hours_per_week',
                  'no_weeks', 'year', 'under_contract', 'start_date',
                  'end_date', 'faculty', 'notes']
        
        widgets = {
            'faculty' : autocomplete.ModelSelect2(url='myprofile:staffmember-autocomplete'),
        }
        model = TeachingTask
        labels = FIELD_LABELS



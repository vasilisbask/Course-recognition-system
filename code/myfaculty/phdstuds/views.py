from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from core import views
from core.views import Table

from .models import PhdThesis, ThesisProgress, Recommendation, JournalPublication, ConferencePublication, TeachingTask
from . import forms
from myprofile.models import Student, PersonalInfo, StaffMember
from django.urls import reverse_lazy
from curricula.models import StudyProgram
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from dal import autocomplete
from scopes.utils import get_secreteriat_scope
from myprofile.checks import is_secreteriat, is_staff_member, is_doctoral_student
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from datetime import datetime
from .email import SUBMITTED_THESIS_REPORT_BODY, SUBMITTED_THESIS_REPORT_SUBJECT
from mailer.gmail import notify
from myprofile.utils import get_domain_uri
from scopes.models import Secretariat

# Create your views here.

"""
Generic phdstuds Views
"""

class SecCreate(views.ScopedSecCreateView):    
    template_name = 'phdstuds/show_object.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user        
        return super().form_valid(form)
        
class SecUpdate(views.ScopedSecUpdateView):    
    template_name = 'phdstuds/show_object.html'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user        
        return super().form_valid(form)

class SecList(views.ScopedSecListView):    
    template_name = 'phdstuds/list_objects.html'

class SecMultipleList(views.SecMultipleListView):
    template_name = 'phdstuds/list_objects.html'

class StaffCreate(views.StaffCreateView):    
    template_name = 'phdstuds/show_object.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user        
        return super().form_valid(form)

class StaffUpdate(views.StaffUpdateView):    
    template_name = 'phdstuds/show_object.html'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user        
        return super().form_valid(form)
    
class StaffList(views.StaffListView):    
    template_name = 'phdstuds/list_objects.html'

class StaffMultipleList(views.StaffMultipleListView):
    template_name = 'phdstuds/list_objects.html'

class StudentCreate(views.DoctoralStudentCreateView):    
    template_name = 'phdstuds/show_object.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user        
        return super().form_valid(form)

class StudentUpdate(views.DoctoralStudentUpdateView):    
    template_name = 'phdstuds/show_object.html'
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user        
        return super().form_valid(form)

class StudentList(views.DoctoralStudentListView):    
    template_name = 'phdstuds/list_objects.html'

class StudentMultipleList(views.DoctoralStudentMultipleListView):
    template_name = 'phdstuds/list_objects.html'

"""
Secretariat Thesis Views
"""
class SecCreatePhDThesis(SecCreate):    
    model = PhdThesis
    form_class = forms.SecThesisForm
    success_url = ''
    headline = _('Δημιουργία Διδακτορικής Διατριβής')
    back_url = ''
    
class SecUpdatePhDThesis(SecUpdate):    
    model = PhdThesis
    form_class = forms.SecThesisForm
    success_url = ''
    headline = _('Ενημέρωση Διδακτορικής Διατριβής')
    delete_url = 'phdstuds:sec_delete_thesis'
    
class SecListPhDThesis(SecList):    
    model = PhdThesis
    fields = ['candidate.surname', 'candidate.given_name', 'subject_gr', 'get_status_display']
    headers = {
        'candidate.surname' : _('Επώνυμο'),
        'candidate.given_name' : _('Όνομα'),        
        'subject_gr' : _('Τίτλος'),
        'get_status_display' : _('Κατάσταση')        
    }    
    table_title = _('Διδακτορικές Διατριβές')    
    create_url = 'phdstuds:sec_create_phd_thesis'
    update_url = 'phdstuds:sec_update_thesis'
    
    extra_buttons = True
    extra_text = _('Υποψήφιος')
    extra_button_icon = 'person'
    extra_url = 'phdstuds:sec_update_phd_student'

    extra_buttons2 = True
    extra_text2 = _('Πορεία')
    extra_button_icon2 = 'school'
    extra_url2 = 'phdstuds:sec_overview_phd_student'

    def get_extra_url(self, obj):
        return reverse_lazy(self.extra_url, kwargs = {'pk' : obj.candidate.pk})
    
    def get_extra_url2(self, obj):
        return reverse_lazy(self.extra_url2, kwargs = {'pk' : obj.candidate.pk})
    
class SecDeletePhDThesis(views.ScopedDeleteView):
    model = PhdThesis 
    success_url = 'phdstuds:sec_list_theses'

"""
Secretariat Student Views
"""

class SecCreatePhDStudent(SecCreate):    
    model = Student
    form_class = forms.SecStudentForm
    success_url = 'phdstuds:sec_list_phd_students'
    headline = _('Δημιουργία Διδακτορικού Φοιτητή')
    back_url = ''
    
class SecUpdatePhDStudent(SecUpdate):    
    model = Student
    form_class = forms.SecStudentForm
    success_url = 'phdstuds:sec_list_phd_students'
    headline = _('Ενημέρωση Στοιχείων Φοίτησης')
    delete_url = 'phdstuds:sec_delete_phd_student'
    headline_above = _('Προσωπικά Στοιχεία')
    above_p = _('Για την ενημέρωση των προσωπικών στοιχείων πατήστε εδώ:')
    button_above_text = _('Επεξεργασία προσωπικών στοιχείων')
    button_above_icon = 'person'
    button_above_classes = 'btn btn-success'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['button_above_url'] = reverse_lazy('phdstuds:sec_update_phd_student_pi',kwargs={"pk": self.object.personal_info.pk})
        return context
        
class SecListPhDStudent(SecList):    
    model = Student
    fields = ['surname', 'given_name', 'email', 'program']
    headers = {
        'surname' : _('Επώνυμο'),
        'given_name' : _('Όνομα'),        
        'email' : _('Email'),
        'program' : _('Πρόγραμμα Σπουδών'),
                
    }    
    table_title = _('Διδακτορικοί Φοιτητές')    
    create_url = 'phdstuds:sec_create_phd_student'
    update_url = 'phdstuds:sec_update_phd_student'
    extra_buttons = True
    extra_text = _('Προφίλ')
    extra_button_icon = 'info'
    extra_url = 'phdstuds:sec_overview_phd_student'
    
    def get_queryset(self):
        return Student.objects.sc_filter(user=self.request.user, program__type=StudyProgram.DOCTORAL)   

class SecDeletePhDStudent(views.ScopedDeleteView):
    model = Student
    success_url = 'phdstuds:sec_list_phd_students'

class SecUpdatePersonalInfo(SecUpdate):    
    model = PersonalInfo
    form_class = forms.SecPersonalInfoForm
    headline = _('Ενημέρωση Προσωπικών Στοιχείων')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse_lazy(
            'phdstuds:sec_update_phd_student', kwargs = {
                'pk': self.object.student_set.first().pk
            }
        )
        return context
    
    def get_success_url(self):
        return reverse_lazy(
            'phdstuds:sec_update_phd_student', kwargs = {
                'pk': self.object.student_set.first().pk
            }
        )
    
"""
Secretariat Report Views
"""
class SecCreateProgress(SecCreate):    
    model = ThesisProgress
    form_class = forms.SecThesisReportForm
    headline = _('Δημιουργία Αναφοράς Υποψήφιου Διδάκτορα')
    
class SecUpdateProgress(SecUpdate):
    model = ThesisProgress
    form_class = forms.SecThesisReportForm
    headline = _('Ενημέρωση Αναφοράς Υποψήφιου Διδάκτορα')
    delete_url = 'phdstuds:sec_delete_progress'
    
class SecListProgress(SecList):    
    model = ThesisProgress
    fields = ['year', 'thesis.candidate.surname', 'thesis.candidate.given_name']
    headers = {
        'thesis.candidate.surname' : _('Επώνυμο'),
        'thesis.candidate.given_name' : _('Όνομα'),        
        'year' : _('Έτος'),        
    }    
    table_title = _('Αναφορές Υποψήφιων Διδακτόρων')    
    create_url = 'phdstuds:sec_create_progress'
    update_url = 'phdstuds:sec_update_progress'
    
class SecDeleteProgress(views.ScopedDeleteView):
    model = ThesisProgress
    success_url = 'phdstuds:sec_list_progress'

"""
Secretariat Recommendation Views
"""
class SecCreateRecommendation(SecCreate):    
    model = Recommendation
    form_class = forms.SecRecommendationForm
    headline = _('Δημιουργία Εισήγησης Προόδου')
    
class SecUpdateRecommendation(SecUpdate):
    model = Recommendation
    form_class = forms.SecRecommendationForm
    headline = _('Ενημέρωση Εισήγησης Προόδου')
    delete_url = 'phdstuds:sec_delete_progress'
    
class SecListRecommendation(SecList):    
    model = Recommendation
    fields = ['year', 'thesis.candidate.surname', 'thesis.candidate.given_name']
    headers = {
        'thesis.candidate.surname' : _('Επώνυμο'),
        'thesis.candidate.given_name' : _('Όνομα'),        
        'year' : _('Έτος'),        
    }    
    table_title = _('Εισηγήσεις Προόδου')    
    create_url = 'phdstuds:sec_create_progress'
    update_url = 'phdstuds:sec_update_progress'
    
class SecDeleteRecommendation(views.ScopedDeleteView):
    model = Recommendation
    success_url = 'phdstuds:sec_list_progress'


"""
Secretariat Journal Publication Views
"""
class SecCreateJournal(SecCreate):    
    model = JournalPublication
    form_class = forms.SecJournalForm
    headline = _('Δημιουργία Δημοσιεύσης')
    
class SecUpdateJournal(SecUpdate):
    model = JournalPublication
    form_class = forms.SecJournalForm
    headline = _('Ενημέρωση Δημοσίευσης')
    delete_url = 'phdstuds:sec_delete_journal'
    
class SecListJournal(SecList):    
    model = JournalPublication
    fields = ['year', 'title', 'journal_title']
    headers = {
        'year' : _('Έτος'),
        'title' : _('Τίτλος'),        
        'journal_title' : _('Περιοδικό'),        
    }    
    table_title = _('Δημοσιεύσεις σε Περιοδικά')    
    create_url = 'phdstuds:sec_create_journal'
    update_url = 'phdstuds:sec_update_journal'
    
class SecDeleteJournal(views.ScopedDeleteView):
    model = JournalPublication
    success_url = 'phdstuds:sec_list_journals'

"""
Secretariat Conference Publication Views
"""
class SecCreateConference(SecCreate):    
    model = ConferencePublication
    form_class = forms.SecConferenceForm
    headline = _('Δημιουργία Δημοσιεύσης')
    
class SecUpdateConference(SecUpdate):
    model = ConferencePublication
    form_class = forms.SecConferenceForm
    headline = _('Ενημέρωση Δημοσίευσης')
    delete_url = 'phdstuds:sec_delete_conference'
    
class SecListConference(SecList):    
    model = ConferencePublication
    fields = ['year', 'title', 'conference_title']
    headers = {
        'year' : _('Έτος'),
        'title' : _('Τίτλος'),        
        'conference_title' : _('Συνέδριο'),        
    }    
    table_title = _('Δημοσιεύσεις σε Συνέδρια')    
    create_url = 'phdstuds:sec_create_conference'
    update_url = 'phdstuds:sec_update_conference'
    
class SecDeleteConference(views.ScopedDeleteView):
    model = ConferencePublication
    success_url = 'phdstuds:sec_list_conferences'

"""
Secretariat Conference Publication Views
"""
class SecCreateConference(SecCreate):    
    model = ConferencePublication
    form_class = forms.SecConferenceForm
    headline = _('Δημιουργία Δημοσιεύσης')
    
class SecUpdateConference(SecUpdate):
    model = ConferencePublication
    form_class = forms.SecConferenceForm
    headline = _('Ενημέρωση Δημοσίευσης')
    delete_url = 'phdstuds:sec_delete_conference'
    
class SecListConference(SecList):    
    model = ConferencePublication
    fields = ['year', 'title', 'conference_title']
    headers = {
        'year' : _('Έτος'),
        'title' : _('Τίτλος'),        
        'conference_title' : _('Συνέδριο'),        
    }    
    table_title = _('Δημοσιεύσεις σε Συνέδρια')    
    create_url = 'phdstuds:sec_create_conference'
    update_url = 'phdstuds:sec_update_conference'
    
class SecDeleteConference(views.ScopedDeleteView):
    model = ConferencePublication
    success_url = 'phdstuds:sec_list_conferences'

"""
Secretariat TeachingTask Publication Views
"""
class SecCreateTeachingTask(SecCreate):    
    model = TeachingTask
    form_class = forms.SecTeachingTaskForm
    headline = _('Δημιουργία Επικουρικού Διδακτικού Έργου')
    
class SecUpdateTeachingTask(SecUpdate):
    model = TeachingTask
    form_class = forms.SecTeachingTaskForm
    headline = _('Ενημέρωση Επικουρικού Διδακτικού Έργου')
    delete_url = 'phdstuds:sec_delete_teachingtask'
    
class SecListTeachingTask(SecList):    
    model = TeachingTask
    fields = ['year', 'course_name', 'faculty']
    headers = {
        'year' : _('Έτος'),
        'course_name' : _('Μάθημα'),        
        'faculty' : _('Υπεύθυνος Καθηγητής'),        
    }    
    table_title = _('Επικουργικό Διδακτικό Έργο')    
    create_url = 'phdstuds:sec_create_teachingtask'
    update_url = 'phdstuds:sec_update_teachingtask'
    
class SecDeleteTeachingTask(views.ScopedDeleteView):
    model = TeachingTask
    success_url = 'phdstuds:sec_list_teachingtasks'


class SecStudentOverviewList(SecMultipleList):
    model = Student
    template_name = 'core/multiple_tables.html'
    master_headline = _('Στοιχεία Διδακτορικής Διατριβής')
    
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        student = Student.objects.get(pk = self.kwargs['pk'])
        self.master_p = _('Υποψήφιος Διδάκτορας: ') + '%s %s' %(student.surname, student.given_name)
        self.tables = [
            Table(
                fields = ['thesis', 'year'],
                table_title = _('Αναφορές Διδακτορικής Διατριβής'),
                headers = {
                    'thesis' : _('Θέμα'),
                    'year' : _('Έτος'),
                },
                table_id = 'progress',
                update_url = 'phdstuds:sec_update_progress',
                create_url = 'phdstuds:sec_create_progress',
                objects = ThesisProgress.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['thesis', 'year'],
                table_title = _('Εισηγήσεις Επιβλέποντα'),
                headers = {
                    'thesis' : _('Θέμα'),
                    'year' : _('Έτος'),
                },
                table_id = 'recommendations',  
                update_url = 'phdstuds:sec_update_recommendation',
                create_url = 'phdstuds:sec_create_recommendation',
                objects = Recommendation.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['title', 'journal_title', 'year'],
                table_title = _('Δημοσιεύσεις σε Περιοδικά'),
                headers = {
                    'title' : _('Τίτλος'),
                    'journal_title' : _('Περιοδικό'),
                    'year' : _('Έτος'),
                },
                table_id = 'journals',   
                update_url = 'phdstuds:sec_update_journal',
                create_url = 'phdstuds:sec_create_journal',
                objects = JournalPublication.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['title','conference_title', 'year'],
                table_title = _('Δημοσιεύσεις σε Συνέδρια'),
                headers = {
                    'title' : _('Τίτλος'),
                    'conference_title' : _('Συνέδριο'),
                    'year' : _('Έτος'),
                },
                table_id = 'conferences',  
                update_url = 'phdstuds:sec_update_conference',
                create_url = 'phdstuds:sec_create_conference',
                objects = ConferencePublication.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['year', 'course_name', 'faculty'],
                headers = {
                    'year' : _('Έτος'),
                    'course_name' : _('Μάθημα'),        
                    'faculty' : _('Υπεύθυνος Καθηγητής'),        
                },    
                table_title = _('Επικουρικό Διδακτικό Έργο'),    
                create_url = 'phdstuds:sec_create_teachingtask',
                update_url = 'phdstuds:sec_update_teachingtask',
                objects = TeachingTask.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            )
        ]

   
"""
Thesis AutoComplete forms
"""

class SecThesisAutoComplete(LoginRequiredMixin, UserPassesTestMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):        
        scopes = get_secreteriat_scope(self.request.user)
        doctoral_progs = scopes['programs'].filter(type = StudyProgram.DOCTORAL)
        if self.q:
            qs = PhdThesis.objects.filter( Q(subject_gr__contains=self.q) | Q(subject_en__contains=self.q) | Q(candidate__surname__contains=self.q), 
                                          candidate__program__in=doctoral_progs )            
        
        return qs[:10]
    
    def test_func(self):
        return is_secreteriat(self.request.user)
    

"""
Staff Student Views
"""

class StaffListPhDThesis(StaffMultipleList):    
    model = PhdThesis
    template_name = 'core/multiple_tables.html'
    master_headline = _('Στοιχεία Διδακτορικής Διατριβής')
    
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        staff_member = get_object_or_404(StaffMember, user=self.request.user)
        self.tables = [
            Table(
                fields = ['candidate.surname', 'candidate.given_name', 'subject_gr', 'get_status_display'],                
                headers = {
                    'candidate.surname' : _('Επώνυμο'),
                    'candidate.given_name' : _('Όνομα'),        
                    'subject_gr' : _('Τίτλος'),
                    'get_status_display' : _('Κατάσταση'),
                },
                table_title = _('Διδακτορικές Διατριβές στις οποίες είστε επιβλέπων'),
                table_id = 'phdsup',
                create_button = False,
                create_url = 'phdstuds:staff_update_thesis',
                update_url = 'phdstuds:staff_update_thesis',
                update_text = _('Λεπτομέρειες'),
                update_button_icon = 'school',
                extra_buttons = True,
                extra_text = _('Προφίλ'),
                extra_button_icon = 'info',
                extra_url = 'phdstuds:staff_overview_phd_student',
                next = self.request.path,                  
                objects = PhdThesis.objects.filter(supervisor = staff_member, candidate__program__type=StudyProgram.DOCTORAL) 
            ),
            Table(
                fields = ['candidate.surname', 'candidate.given_name', 'subject_gr', 'get_status_display'],                
                headers = {
                    'candidate.surname' : _('Επώνυμο'),
                    'candidate.given_name' : _('Όνομα'),        
                    'subject_gr' : _('Τίτλος'),
                    'get_status_display' : _('Κατάσταση'),
                },
                table_title = _('Διδακτορικές Διατριβές στις οποίες είστε στην επιτροπή παρακολούθησης'),
                create_button = False,
                create_url = 'phdstuds:staff_update_thesis',
                update_url = 'phdstuds:staff_update_thesis',
                update_text = _('Λεπτομέρειες'),
                update_button_icon = 'school',
                extra_buttons = True,
                table_id = 'phdcom',
                extra_text = _('Προφίλ'),
                extra_button_icon = 'info',
                extra_url = 'phdstuds:staff_overview_phd_student',
                next = self.request.path,  
                objects = PhdThesis.objects.filter(committee = staff_member, candidate__program__type=StudyProgram.DOCTORAL) 
            ),

        ]
   
    def test_func(self):
        return is_staff_member(self.request.user)  

class StaffListRecommendations(StaffList):    
    model = PhdThesis
    fields = ['year', 'thesis.candidate.surname', 'thesis.candidate.given_name']
    headers = {
        'thesis.candidate.surname' : _('Επώνυμο'),
        'thesis.candidate.given_name' : _('Όνομα'),        
        'year' : _('Έτος'),
                
    }    
    table_title = _('Εισηγήσεις Διδακτορικών Διατριβών')    
    create_button = True
    create_button_text = _('Νέα Εισήγηση')
    create_url = 'phdstuds:staff_create_recommendation_generic'
    update_url = 'phdstuds:staff_update_recommendation'
    update_text = _('Λεπτομέρειες')
    update_button_icon = 'school'
    
    def get_queryset(self):
        staff_member = get_object_or_404(StaffMember, user = self.request.user)
        return Recommendation.objects.filter(recommender = staff_member) 
       
    def test_func(self):
        return is_staff_member(self.request.user)  
    
class StaffUpdatePhDThesis(StaffUpdate):    
    model = PhdThesis
    form_class = forms.StaffThesisForm
    headline = _('Ενημέρωση Διδακτορικής Διατριβής')
    delete_url = None

    def get_object(self, queryset = None):
        object = super().get_object(queryset=queryset)
        staff_member = get_object_or_404(StaffMember, user = self.request.user)        
        if object.supervisor != staff_member and not (staff_member in object.committee.all() ):
            raise PermissionDenied
        return object
    
    def test_func(self):
        return is_staff_member(self.request.user)  

class StaffThesisModelView(StaffUpdate):
    model = None
    form_class = None
    delete_url = None

    def get_object(self, queryset = None):
        object = super().get_object(queryset=queryset)
        staff_member = get_object_or_404(StaffMember, user = self.request.user)        
        if object.thesis.supervisor != staff_member and not (staff_member in object.thesis.committee.all()):
            raise PermissionDenied
        return object

class StaffUpdateProgress(StaffThesisModelView):    
    model = ThesisProgress
    form_class = forms.StaffReportForm
    headline = _('Αναφορά Πορείας Διδακτορικής Διατριβής')

class StaffUpdateRecommendation(StaffThesisModelView):    
    model = Recommendation
    form_class = forms.StaffRecommendationForm
    headline = _('Εισήγηση Πορείας Διδακτορικής Διατριβής')

class StaffCreateRecommendationGeneric(StaffCreate):

    model = Recommendation
    form_class = forms.StaffCreateRecommendationForm
    headline = _('Δημιουργία Εισήγησης Πορείας Διδακτορικής Διατριβής')

    def form_valid(self, form):
        instance = form.save(commit=False)        
        staff_member = get_object_or_404(StaffMember, user=self.request.user)
        instance.recommender = staff_member
        instance.save()        
        return super().form_valid(form)
    
class StaffCreateRecommendation(StaffCreateRecommendationGeneric):
    model = Recommendation
    form_class = forms.StaffCreateRecommendationForm

    def get_form(self, *args, **kwargs):
        thesis_pk = self.kwargs.get('pk')
        staff_member = get_object_or_404(StaffMember, user=self.request.user)
        thesis = get_object_or_404(PhdThesis, pk = thesis_pk, supervisor = staff_member)
        form = super().get_form(*args, **kwargs)
        form.fields['thesis'].initial = thesis
        form.fields['thesis'].disabled = True
        return form

class StaffUpdateJournal(StaffThesisModelView):    
    model = JournalPublication
    form_class = forms.StaffJournalForm
    headline = _('Δημοσίευση σε Περιοδικό')

class StaffUpdateConference(StaffThesisModelView):    
    model = ConferencePublication
    form_class = forms.StaffConferenceForm
    headline = _('Δημοσίευση σε Συνέδριο')

class StaffUpdateTeachingTask(StaffThesisModelView):    
    model = TeachingTask
    form_class = forms.StaffTeachingTaskForm
    headline = _('Επικουρικό Έργο')
            
class StaffStudentOverviewList(StaffMultipleList):
    model = Student
    template_name = 'phdstuds/multiple_tables.html'
    master_headline = _('Στοιχεία Διδακτορικής Διατριβής')
    
    def test_func(self):
        return is_staff_member(self.request.user)  
    
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        staff_member = get_object_or_404(StaffMember, user=self.request.user)
        phd_thesis = get_object_or_404(PhdThesis, pk=self.kwargs['pk'])
        if (phd_thesis.supervisor != staff_member) and not (staff_member in phd_thesis.committee.all() ):
            raise PermissionDenied
        
        create_new_recommendation = (phd_thesis.supervisor == staff_member)
        
        student = phd_thesis.candidate
        self.master_p = _('Υποψήφιος Διδάκτορας: ') + '%s %s' %(student.surname, student.given_name)
        self.tables = [
            Table(
                fields = ['thesis', 'year'],
                table_title = _('Αναφορές Διδακτορικής Διατριβής'),
                headers = {
                    'thesis' : _('Θέμα'),
                    'year' : _('Έτος'),
                },
                table_id = 'progress',
                create_button = False,
                update_url = 'phdstuds:staff_update_progress',   
                update_button_icon = 'info',
                update_text = _('Λεπτομέρειες'),             
                objects = ThesisProgress.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['thesis', 'year'],
                table_title = _('Εισηγήσεις Επιβλέποντα'),
                headers = {
                    'thesis' : _('Θέμα'),
                    'year' : _('Έτος'),
                },
                table_id = 'recommendations',  
                update_url = 'phdstuds:staff_update_recommendation',
                update_button_icon = 'info',
                update_text = _('Λεπτομέρειες'),             
                create_button = create_new_recommendation,
                create_url = reverse_lazy('phdstuds:staff_create_recommendation', kwargs = {'pk' : phd_thesis.pk}),
                create_text = 'Νέα εισήγηση',
                objects = Recommendation.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['title', 'journal_title', 'year'],
                table_title = _('Δημοσιεύσεις σε Περιοδικά'),
                headers = {
                    'title' : _('Τίτλος'),
                    'journal_title' : _('Περιοδικό'),
                    'year' : _('Έτος'),
                },
                table_id = 'journals',   
                create_button = False,               
                update_button_icon = 'info',
                update_text = _('Λεπτομέρειες'),
                update_url = 'phdstuds:staff_update_journal',
                objects = JournalPublication.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['title','conference_title', 'year'],
                table_title = _('Δημοσιεύσεις σε Συνέδρια'),
                headers = {
                    'title' : _('Τίτλος'),
                    'conference_title' : _('Συνέδριο'),
                    'year' : _('Έτος'),
                },
                table_id = 'conferences',  
                create_button = False,               
                update_url = 'phdstuds:staff_update_conference',
                update_button_icon = 'info',
                update_text = _('Λεπτομέρειες'),             
                objects = ConferencePublication.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['year', 'course_name', 'faculty'],
                headers = {
                    'year' : _('Έτος'),
                    'course_name' : _('Μάθημα'),        
                    'faculty' : _('Υπεύθυνος Καθηγητής'),        
                },    
                table_title = _('Επικουρικό Διδακτικό Έργο'),    
                update_url = 'phdstuds:staff_update_teachingtask',
                create_button = False,                
                objects = TeachingTask.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            )
        ]

"""
Student views
"""

class StudentThesisModelUpdateView(StudentUpdate):
    model = None
    form_class = None
    delete_url = None

    def get_object(self, queryset = None):
        object = super().get_object(queryset=queryset)
        student = get_object_or_404(Student, user = self.request.user, program__type = StudyProgram.DOCTORAL)
        if object.thesis.candidate != student:
            raise PermissionDenied
        return object

class StudentThesisModelCreateView(StudentCreate):
    model = None
    form_class = None
    delete_url = None

    def form_valid(self, form):
        student = get_object_or_404(Student, 
                                    user=self.request.user, 
                                    program__type = StudyProgram.DOCTORAL)
        thesis = get_object_or_404(PhdThesis, candidate = student)
        form.instance.thesis = thesis                
        return super().form_valid(form)

class StudentUpdateProgress(StudentThesisModelUpdateView):    
    model = ThesisProgress
    form_class = forms.StudentUpdateReportForm
    headline = _('Αναφορά Πορείας Διδακτορικής Διατριβής')

class StudentCreateProgress(StudentThesisModelCreateView):    
    model = ThesisProgress
    form_class = forms.StudentCreateReportForm
    headline = _('Αναφορά Πορείας Διδακτορικής Διατριβής')
    confirm_modal = True

    def form_valid(self, form):
        response = super().form_valid(form)
        supervisor_email = self.object.thesis.supervisor.email
        year = self.object.year
        student = self.object.thesis.candidate
        msg = SUBMITTED_THESIS_REPORT_BODY.format(
            given_name = student.given_name,
            surname = student.surname,
            year = year,
            url = get_domain_uri(self.request)
        )
        
        # Notification emails
        notify.delay(supervisor_email, SUBMITTED_THESIS_REPORT_SUBJECT, msg)
        
        for committee_member in self.object.thesis.committee.all():
            committee_member_email = committee_member.email
            notify.delay(committee_member_email, SUBMITTED_THESIS_REPORT_SUBJECT, msg)
        
        secretaries = Secretariat.objects.filter(programs = student.program)
        for secretary in secretaries.all():
            secretary_email = secretary.user.email
            notify.delay(secretary_email, SUBMITTED_THESIS_REPORT_SUBJECT, msg)
            
        return response


class StudentUpdateRecommendation(StudentThesisModelUpdateView):    
    model = Recommendation
    form_class = forms.StudentRecommendationForm
    headline = _('Εισήγηση Πορείας Διδακτορικής Διατριβής')
    

class StudentCreateJournal(StudentThesisModelCreateView):    
    model = JournalPublication
    form_class = forms.StudentJournalForm
    headline = _('Δημοσίευση σε Περιοδικό')

class StudentUpdateJournal(StudentThesisModelUpdateView):    
    model = JournalPublication
    form_class = forms.StudentJournalForm
    headline = _('Δημοσίευση σε Περιοδικό')

class StudentCreateConference(StudentThesisModelCreateView):    
    model = ConferencePublication
    form_class = forms.StudentConferenceForm
    headline = _('Δημοσίευση σε Συνέδριο')

class StudentUpdateConference(StudentThesisModelUpdateView):    
    model = ConferencePublication
    form_class = forms.StudentConferenceForm
    headline = _('Δημοσίευση σε Συνέδριο')

class StudentCreateTeachingTask(StudentThesisModelCreateView):    
    model = TeachingTask
    form_class = forms.StudentTeachingTaskForm
    headline = _('Επικουρικό Έργο')

class StudentUpdateTeachingTask(StudentThesisModelUpdateView):    
    model = TeachingTask
    form_class = forms.StudentTeachingTaskForm
    headline = _('Επικουρικό Έργο')
            
class StudentOverviewList(StudentMultipleList):
    model = Student
    template_name = 'core/multiple_tables.html'
    master_headline = _('Στοιχεία Διδακτορικής Διατριβής')
    
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        student = get_object_or_404(Student, user = self.request.user, program__type = StudyProgram.DOCTORAL)
        phd_thesis = get_object_or_404(PhdThesis, candidate = student)
        self.master_p = _('Βεβαιωθείτε ότι τα προσωπικά σας στοιχεία είναι ενημερώμενα')
        self.master_button = True
        self.master_url = 'phdstuds:stud_update_pi'
        self.master_button_class = 'btn btn-success'
        self.master_button_icon = 'account_circle'
        self.master_text = _('Προσωπικά Στοιχεία')
        self.tables = [
            Table(
                fields = ['thesis', 'year'],
                table_title = _('Αναφορές Διδακτορικής Διατριβής'),
                headers = {
                    'thesis' : _('Θέμα'),
                    'year' : _('Έτος'),
                },
                table_id = 'progress',
                create_button = True,
                create_text = _('Νέα Αναφορά'),
                create_url = 'phdstuds:stud_create_progress',
                update_url = 'phdstuds:stud_update_progress',  
                update_text = 'Προβολή',
                update_button_icon = 'visibility',  
                update_button_class = 'btn btn-success',            
                objects = ThesisProgress.objects.filter(thesis__candidate = student),
                next = self.request.path, 
                
            ),
            Table(
                fields = ['thesis', 'year'],
                table_title = _('Εισηγήσεις Επιβλέποντα'),
                headers = {
                    'thesis' : _('Θέμα'),
                    'year' : _('Έτος'),
                },
                table_id = 'recommendations',  
                update_url = 'phdstuds:stud_update_recommendation',
                update_text = 'Προβολή',
                update_button_icon = 'visibility',  
                update_button_class = 'btn btn-success',           
                create_button = False,
                objects = Recommendation.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['title', 'journal_title', 'year'],
                table_title = _('Δημοσιεύσεις σε Περιοδικά'),
                headers = {
                    'title' : _('Τίτλος'),
                    'journal_title' : _('Περιοδικό'),
                    'year' : _('Έτος'),
                },
                table_id = 'journals',   
                create_button = True,
                create_text = 'Νέο Περιοδικό',
                create_url = 'phdstuds:stud_create_journal',                          
                update_url = 'phdstuds:stud_update_journal',
                update_text = 'Προβολή',
                update_button_icon = 'visibility',  
                update_button_class = 'btn btn-success',            
                objects = JournalPublication.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['title','conference_title', 'year'],
                table_title = _('Δημοσιεύσεις σε Συνέδρια'),
                headers = {
                    'title' : _('Τίτλος'),
                    'conference_title' : _('Συνέδριο'),
                    'year' : _('Έτος'),
                },
                table_id = 'conferences',  
                create_button = True,       
                create_text = _('Νέα Συνέδριο'),        
                create_url = 'phdstuds:stud_create_conference',
                update_url = 'phdstuds:stud_update_conference',
                update_text = _('Προβολή'),
                update_button_icon = 'visibility',  
                update_button_class = 'btn btn-success',           
                objects = ConferencePublication.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            ),
            Table(
                fields = ['year', 'course_name', 'faculty'],
                headers = {
                    'year' : _('Έτος'),
                    'course_name' : _('Μάθημα'),        
                    'faculty' : _('Υπεύθυνος Καθηγητής'),        
                },    
                table_title = _('Επικουρικό Διδακτικό Έργο'),    
                update_url = 'phdstuds:stud_update_teachingtask',
                create_button = True,
                create_text = _('Νέο Επικουρικό Έργο'),
                create_url = 'phdstuds:stud_create_teachingtask',
                update_text = _('Προβολή'),
                update_button_icon = 'visibility',  
                update_button_class = 'btn btn-success',            
                objects = TeachingTask.objects.filter(thesis__candidate = student),
                next = self.request.path,  
            )
        ]

class StudentDeleteTeachingTask(views.DoctoralStudentUpdateView):
    model = TeachingTask
    success_url = 'phdstuds:stud_overview'

class StudentDeleteJournal(views.DoctoralStudentUpdateView):
    model = JournalPublication
    success_url = 'phdstuds:stud_overview'

class StudentDeleteConference(views.DoctoralStudentUpdateView):
    model = ConferencePublication
    success_url = 'phdstuds:stud_overview'

class StudentPI(views.DoctoralStudentUpdateView):
    model = PersonalInfo
    success_url = 'phdstuds:stud_overview'
    form_class = forms.StudentPersonalInfoForm
    headline = _('Ενημέρωση προσωπικών στοιχείων')
    def get_object(self, queryset = None):
        student = get_object_or_404(Student, program__type=StudyProgram.DOCTORAL, user = self.request.user)
        return student.personal_info
        
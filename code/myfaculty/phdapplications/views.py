from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse
from myprofile.checks import is_staff_member, is_doctoral_secreteriat
from .models import Call, Application, Degree, JournalPublication, ConferencePublication, WorkExperience, ReferenceContact, ReferenceLetter, Applicant, AppPersonalInfo
import phdapplications.forms as forms
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.signing import TimestampSigner,SignatureExpired, BadSignature
from django.conf import settings
from myprofile.models import StaffMember
from django.core.exceptions import PermissionDenied
from datetime import datetime
from django.http import Http404
from .utils import get_or_create_object, inform_for_submission, inform_for_rf
from django.utils.translation import gettext_lazy as _
from export.models import DocumentTemplate
from core.views import GenericDeleteView, ScopedSecCreateView, GenericCreateView, GenericUpdateView, Table, ScopedSecUpdateView
from .utils import get_or_create_application, pi_is_complete, check_application, invite_reviewers, build_application_pdf
from django.utils import timezone
from myprofile.checks import can_review_phd_apps, can_apply_for_phd

# Create your views here.

def has_doctoral_applicant_profile(user):
    return Applicant.objects.filter(user=user).exists()

def can_apply_for_phd_and_has_profile(user):
    return has_doctoral_applicant_profile(user) and can_apply_for_phd(user)

# check if PI fields are completed

def table_context(tables):
    context = {
        'tables' : []
    }
    for name, table in enumerate(tables):
        table_context = table.to_context()
        context['tables'].append(table_context)
    return context

def update_application_url(application):
    return reverse_lazy('phdapplications:apply', kwargs = {'pk' : application.call.pk})

@login_required
@user_passes_test(can_apply_for_phd)
def dashboard(request):
    template_name = 'core/multiple_tables.html'
    applicant = get_or_create_object(Applicant, user=request.user )
    calls_open = Call.objects.open_for_application()
    
    applications_draft = Application.objects.filter(
        status = Application.DRAFT, 
        applicant = applicant)
    
    applications_submitted = Application.objects.filter(
        status = Application.SUBMITTED,
        applicant = applicant)
    
    tables = [
         Table( 
            fields = ['title', 'program.department', 'supervisor'],
            table_title = _('Ανοιχτές Προσκλήσεις'),
            headers = {
                'title' : _('Θέμα'),
                'program.department' : _('Τμήμα'),
                'supervisor' : _('Επιβλέπων'),
            },
            table_id = 'open',
            next = request.path,
            create_button = False,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility', 
            update_url = 'phdapplications:view_call',
            extra_text = _('Αίτηση'),
            extra_url = 'phdapplications:apply',
            extra_button_icon = 'star',
            extra_buttons = True,          
            objects = calls_open
        ),       
        Table( 
            fields = ['rf', 'call.title', 'call.program.department'],
            table_title = _('Αιτήσεις σε προσωρινή αποθήκευση'),
            headers = {
                'rf' : _('Αριθμός αναφοράς'),
                'call.title' : _('Πρόσκληση'),
                'call.program.department' : _('Τμήμα'),
            },
            table_id = 'draft',
            next = request.path,
            create_button = False,
            update_url_callable = update_application_url,
            objects = applications_draft
        ),
        Table( 
            fields = ['rf', 'call.title', 'call.program.department'],
            table_title = _('Αιτήσεις που έχουν υποβληθεί'),
            headers = {
                'rf' : _('Αριθμός αναφοράς'),
                'call.title' : _('Πρόσκληση'),
                'call.program.department' : _('Τμήμα'),
            },
            table_id = 'submitted',
            next = request.path,
            create_button = False,
            update_url_callable = update_application_url,
            objects = applications_submitted
        )
    ]
    context = table_context(tables)
    context['profile'] = applicant
    
    return render(request, template_name, context = context)

@login_required
@user_passes_test(can_apply_for_phd_and_has_profile)
def list_contacts(request, app_pk):
    template_name = 'phdapplications/candidate_app_rc.html'
    applicant = get_object_or_404(Applicant, user=request.user)
    application = get_object_or_404(Application, pk = app_pk, applicant = applicant)
    
    tables = [
        Table(
            fields = ['given_name', 'surname', 'institution', 'status'],
            table_title = _('Σημεία Επαφής για Παροχή Συστατικής Επιστολής'),
            headers = {
                'given_name' : _('Όνομα'),
                'surname' : _('Επώνυμο'),
                'institution' : _('Φορέας'),
                'status' : _('Κατάσταση Συστατικής'),
            },
            table_id = 'contacts',
            update_url = 'phdapplications:applicant_update_contact',
            create_url = reverse_lazy('phdapplications:applicant_create_contact', kwargs = {'app_pk' : application.pk }),
            objects = ReferenceContact.objects.filter(application = application),
            next = request.path,
            create_text = 'Νέo Σημείο Επαφής',
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility'
        )        
    ]
    context = table_context(tables)
    context['back_url'] = reverse_lazy('phdapplications:apply', kwargs={'pk' : application.call.pk})
    return render(request, template_name, context=context)

class ApplicantCreate(GenericCreateView):

    def test_func(self):
        return can_apply_for_phd_and_has_profile(self.request.user)
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        applicant = get_object_or_404(Applicant, 
                                      user = self.request.user)
        self.application = get_object_or_404(Application, 
                                             pk = self.kwargs['app_pk'],
                                             applicant = applicant)
    def form_valid(self, form):
        form.instance.application = self.application
        return super().form_valid(form)

class ApplicantUpdate(GenericUpdateView):

    def test_func(self):
        return can_apply_for_phd_and_has_profile(self.request.user)

    def get_object(self, queryset = None):
        applicant = get_object_or_404(Applicant, 
                                      user = self.request.user)
        object = get_object_or_404(self.model,
                                   pk = self.kwargs['pk'])
        
        if hasattr(object, 'applicant'):
            obj_applicant = object.applicant
        else:
            obj_applicant = object.application.applicant

        if obj_applicant != applicant:
            raise PermissionDenied
        
        return object
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.object.applicant_can_delete():
            context['delete_url'] = None
        
        return context
    
class update_pi(ApplicantUpdate):
    model = AppPersonalInfo
    form_class = forms.CandidatePIFrom

    def get_success_url(self, *args, **kwargs):
        application = get_object_or_404(Application, pi = self.object)
        return reverse_lazy('phdapplications:apply', kwargs={'pk' : application.call.pk })
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not pi_is_complete(self.object):
            context['msg'] = _('Παρακαλούμε συμπληρώστε τα στοιχεία που λείπουν παρακάτω για να συνεχίσετε.')
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

@login_required
def apply(request, pk):
    template_name = 'phdapplications/candidate_app.html'

    user = request.user
    call = get_object_or_404(Call, pk = pk)
    app = get_or_create_application(user, call=call)
    pi = app.pi
    if not pi_is_complete(pi):
        return redirect('phdapplications:update_pi', pk = pi.pk)

    context = {
        'application' : app,
        'profile' : pi,
        'app_url' : reverse_lazy('phdapplications:application_main', kwargs = {'pk' : app.pk}),
        'extra_url' : reverse_lazy('phdapplications:application_extra', kwargs = {'pk' : app.pk}),
        'pi_url' : reverse_lazy('phdapplications:update_pi', kwargs = {'pk' : pi.pk}),                      
        'rc_url' : reverse_lazy('phdapplications:applicant_list_contacts', kwargs = {'app_pk' : app.pk}),
        'next' : request.path,
        'back_url' : reverse_lazy('phdapplications:applicant_dashboard'),
    }
    if app.applicant_can_submit():
        context['submit_url'] = reverse_lazy('phdapplications:submit', kwargs = {'pk' : app.pk})                      
    
    if app.applicant_can_delete():
        context['delete_url'] = reverse_lazy('phdapplications:delete', kwargs = {'pk' : app.pk})                    
    
    return render(request, template_name, context=context)

class application_main(ApplicantUpdate):
    
    model = Application
    form_class = forms.CandidateUpdateApplicationForm
    template_name = 'phdapplications/application_main.html'
    headline = ('Η αίτηση σας')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.object
        return context
    
    def test_func(self):
        return has_doctoral_applicant_profile(self.request.user)
    

@login_required
@user_passes_test(can_apply_for_phd_and_has_profile)
def apply_extra_info(request, pk):

    template_name = 'phdapplications/candidate_app_extra.html'
    applicant = get_object_or_404(Applicant, user = request.user)
    application = get_object_or_404(Application, applicant=applicant, pk=pk)
    
    tables = [
        Table(
            fields = ['year','get_type_display','department'],
            table_title = _('Πτυχία'),
            headers = {
                'year' : _('Έτος'),
                'get_type_display' : _('Τύπος'),
                'department' : _('Τμήμα'),                
            },
            table_id = 'degrees',
            update_url = 'phdapplications:applicant_update_degree',
            create_url = reverse_lazy('phdapplications:applicant_create_degree', kwargs = {'app_pk' : application.pk }),
            objects = Degree.objects.filter(application = application),
            next = request.path,
            create_text = 'Νέο Πτυχίο',
        ),
        Table(
            fields = ['start_date.year','title','company'],
            table_title = _('Εργασιακή Εμπειρία'),
            headers = {
                'start_date.year' : _('Έτος Έναρξης'),
                'title' : _('Τίτλος'),
                'company' : _('Φορέας'),
            },
            table_id = 'workexp',
            update_url = 'phdapplications:applicant_update_workexp',
            create_url = reverse_lazy('phdapplications:applicant_create_workexp', kwargs = {'app_pk' : application.pk }),
            objects = WorkExperience.objects.filter(application = application),
            next = request.path,
            create_text = 'Νέα Εργασιακή Εμπειρία',
        ),
        Table(
            fields = ['year','title','journal_title'],
            table_title = _('Δημοσιεύσεις σε Περιοδικά'),
            headers = {
                'year' : _('Έτος'),
                'title' : _('Τίτλος'),
                'journal_title' : _('Περιοδικό'),
            },
            table_id = 'journals',
            update_url = 'phdapplications:applicant_update_journal',
            create_url = reverse_lazy('phdapplications:applicant_create_journal', kwargs = {'app_pk' : application.pk }),
            objects = JournalPublication.objects.filter(application = application),
            next = request.path,
            create_text = 'Νέο Περιοδικό',
        ),
        Table(
            fields = ['year','title','conference_title'],
            table_title = _('Δημοσιεύσεις σε Συνέδρια'),
            headers = {
                'year' : _('Έτος'),
                'title' : _('Τίτλος'),
                'conference_title' : _('Συνέδριο'),
            },
            table_id = 'conferences',
            update_url = 'phdapplications:applicant_update_conference',
            create_url = reverse_lazy('phdapplications:applicant_create_conference', kwargs = {'app_pk' : application.pk }),
            objects = ConferencePublication.objects.filter(application = application),
            next = request.path,
            create_text = 'Νέο Συνέδριο',
        ),
    ]
    context = table_context(tables)
    context['application'] = application
    context['back_url'] = reverse_lazy('phdapplications:apply', kwargs={'pk' : application.call.pk})
    
    return render(request, template_name, context=context)
    

        
class create_degree(ApplicantCreate):
    model = Degree
    form_class = forms.CandidateDegreeForm
    headline = _('Στοιχεία τίτλου σπουδών')

class update_degree(ApplicantUpdate):
    model = Degree
    form_class = forms.CandidateDegreeForm
    headline = _('Στοιχεία τίτλου σπουδών')
    delete_url = 'phdapplications:applicant_delete_degree'

class create_workexp(ApplicantCreate):
    model = WorkExperience
    form_class = forms.CandidateExperienceForm
    headline = _('Στοιχεία εργασιακής εμπειρίας')

class update_workexp(ApplicantUpdate):
    model = WorkExperience
    form_class = forms.CandidateExperienceForm
    headline = _('Στοιχεία εργασιακής εμπειρίας')
    delete_url = 'phdapplications:applicant_delete_experience'
    
class create_journal(ApplicantCreate):
    model = JournalPublication
    form_class = forms.CandidateJournalForm
    headline = _('Στοιχεία δημοσιεύσης')

class update_journal(ApplicantUpdate):
    model = JournalPublication
    form_class = forms.CandidateJournalForm
    headline = _('Στοιχεία δημοσιεύσης')
    delete_url = 'phdapplications:applicant_delete_journal'

class create_conference(ApplicantCreate):
    model = ConferencePublication
    form_class = forms.CandidateConferenceForm
    headline = _('Στοιχεία δημοσιεύσης')

class update_conference(ApplicantUpdate):
    model = ConferencePublication
    form_class = forms.CandidateConferenceForm
    headline = _('Στοιχεία δημοσιεύσης')
    delete_url = 'phdapplications:applicant_delete_conference'

class create_contact(ApplicantCreate):
    model = ReferenceContact
    form_class = forms.CandidateContactForm
    headline = _('Στοιχεία σημείου επαφής')

class update_contact(ApplicantUpdate):
    model = ReferenceContact
    form_class = forms.CandidateContactForm
    headline = _('Στοιχεία σημείου επαφής')
    delete_url = 'phdapplications:applicant_delete_contact'
    
class view_call(GenericUpdateView):
    headline = _('Λεπτομέρειες Πρόσκλησης')
    model = Call
    form_class = forms.DisabledCallForm
    
@login_required
@user_passes_test(can_apply_for_phd_and_has_profile)
def submit(request, pk):
    template_name = 'phdapplications/submit.html'
    applicant = get_object_or_404(Applicant, user = request.user)
    application = get_object_or_404(Application, pk = pk, applicant = applicant)
    result = check_application(application)
    can_submit = application.applicant_can_submit()
    url = reverse_lazy('phdapplications:apply', kwargs = {'pk' : application.call.pk })


    if request.method == 'POST':
        if len(result['errors']) == 0:
            application.status = Application.SUBMITTED
            application.date_submitted = timezone.now()
            inform_for_submission(application)
            application.save()
            invite_reviewers(request, application)
            return redirect(url)
        
    return render(request, template_name, context = 
                  {'result' : result,
                   'can_submit' : can_submit,
                   'application' : application,
                   'back_url' : url})

class CandidateDeleteView(GenericDeleteView):

    def can_delete(self, object):
        return object.applicant_can_delete()

class candidate_delete_application(CandidateDeleteView):
    model = Application
    success_url = 'phdapplications:applicant_dashboard'

class candidate_delete_degree(CandidateDeleteView):
    model = Degree

class candidate_delete_experience(CandidateDeleteView):
    model = WorkExperience

class candidate_delete_contact(CandidateDeleteView):
    model = ReferenceContact

    def can_delete(self, object):
        return super().can_delete(object) and (object.status() == ReferenceContact.NOT_NOTIFIED)

class candidate_delete_journal(CandidateDeleteView):
    model = JournalPublication

class candidate_delete_conference(CandidateDeleteView):
    model = ConferencePublication
    
def reference_letter(request, token):
    signer = TimestampSigner()
    try:
        invitation = signer.unsign_object(token,max_age = settings.INVITATION_REFERENCE_MAX_AGE_SECS)
    except SignatureExpired:
        message = _("""
            H πρόκληση για να υποβάλλετε την συστατική έχει λήξει.
            """)
        return render(request,'phdapplications/message.html', context = {'message' : message})        
    except BadSignature:
        message = _("""
            O σύνδεσμος δεν είναι σωστός!
            """)
        return render(request,'phdapplications/message.html', context = {'message' : message})  
        
    application_id = invitation['application_id']
    contact_id = invitation['contact_id']

    contact = get_object_or_404(ReferenceContact, id = contact_id)
    application = get_object_or_404(Application, id = application_id)
    applicant = application.applicant
    call = application.call
    
    ref_letters = ReferenceLetter.objects.filter(contact = contact)
    if ref_letters.exists():
        old_instance = ref_letters.first()
    else:
        old_instance = None
    
    if request.method == "POST":        
        form = forms.ReferenceLetterForm(request.POST, request.FILES, instance=old_instance)
        if form.is_valid():
            now = timezone.now()
            instance = form.save(commit=False)
            instance.contact = contact
            instance.application = application
            instance.email = contact.email
            instance.submitted_date = now
            instance.save()
            contact.responded_on = now
            contact.responded = True
            contact.save()
            return render(request,'phdapplications/message.html', context = {'message' : _('Ευχαριστούμε πολύ! Η συστατική σας καταχωρήθηκε.')}) 
    else:
        
        if ref_letters.count() == 0:
            initial_values = {        
                'email': contact.email,
                'phone': contact.phone,
                'surname': contact.surname,
                'given_name': contact.given_name,
                'title': contact.title,
                'institution' : contact.institution,
            }
            form = forms.ReferenceLetterForm(initial_values=initial_values)
        else:
            form = forms.ReferenceLetterForm(instance = ref_letters.first() )

    return render(request,'phdapplications/reference_letter.html', context = {'contact' : contact, 'form' : form, 'application' : application, 'call' : call, 'applicant' : applicant})




@login_required
@user_passes_test(is_staff_member)
def rev_dashboard(request):
    template_name = 'core/multiple_tables.html'
    staff_member = get_object_or_404(StaffMember, user=request.user)
    calls_open = Call.objects.open_for_application().filter(reviewers = staff_member)
    calls_expired = Call.objects.expired().filter(reviewers = staff_member)

    tables = [
        Table( 
            fields = ['title', 'program.department', 'supervisor'],
            table_title = _('Ανοιχτές Προσκλήσεις'),
            headers = {
                'title' : _('Θέμα'),
                'program.department' : _('Τμήμα'),
                'supervisor' : _('Επιβλέπων'),
            },
            table_id = 'open',
            next = request.path,
            create_button = False,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility', 
            update_url = 'phdapplications:view_call',
            extra_text = _('Αίτησεις'),
            extra_url = 'phdapplications:rev_list_applications',
            extra_button_icon = 'docs',
            extra_buttons = True,          
            objects = calls_open
        ), 
        Table( 
            fields = ['title', 'program.department', 'supervisor'],
            table_title = _('Προσκλήσεις που έχουν λήξει'),
            headers = {
                'title' : _('Θέμα'),
                'program.department' : _('Τμήμα'),
                'supervisor' : _('Επιβλέπων'),
            },
            table_id = 'closed',
            next = request.path,
            create_button = False,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility', 
            update_url = 'phdapplications:view_call',
            extra_text = _('Αίτησεις'),
            extra_url = 'phdapplications:rev_list_applications',
            extra_button_icon = 'docs',
            extra_buttons = True,          
            objects = calls_expired
        ), 
    ]
    context = table_context(tables)
    return render(request, template_name, context = context)

@login_required
@user_passes_test(is_staff_member)
def rev_applications(request, pk):
    template_name = 'phdapplications/applications.html'
    staff_member = get_object_or_404(StaffMember, user=request.user)
    call = get_object_or_404(Call, pk = pk,reviewers = staff_member)
    applications = Application.objects.filter(call = call).exclude(status=Application.DRAFT).order_by('-date_submitted')    
    tables = [
        Table( 
            fields = ['applicant.given_name', 'applicant.surname', 'date_submitted.date', 'get_status_display'],
            table_title = _('Αιτήσεις'),
            headers = {
              'applicant.given_name' : _('Όνομα'), 
              'applicant.surname' : _('Επώνυμο'),
              'date_submitted.date' : _('Ημερομηνία Υποβολής'),
              'get_status_display': _('Κατάσταση'),
            },
            table_id = 'applications',
            next = request.path,
            create_button = False,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility', 
            update_url = 'phdapplications:rev_application',
            objects = applications
        ), 
    ]
    context = table_context(tables)
    context['call'] = call
    context['back_url'] = reverse_lazy('phdapplications:rev_dashboard')
    return render(request, template_name, context = context)

@login_required
@user_passes_test(is_staff_member)
def rev_application(request, pk):
    template_name = 'phdapplications/reviewer_app.html'
    staff_member = get_object_or_404(StaffMember, user=request.user)
    app = get_object_or_404(Application, call__reviewers = staff_member, pk = pk)
    back_url = request.GET.get(
                'next',
                reverse_lazy('phdapplications:rev_dashboard')
                )
    
    return render(request, template_name, 
                  context={
                      'application' : app,
                      'profile' : app.pi,
                      'app_url' : reverse_lazy('phdapplications:rev_application_main', kwargs = {'pk' : app.pk}),
                      'extra_url' : reverse_lazy('phdapplications:rev_application_extra', kwargs = {'pk' : app.pk}),
                      'pi_url' : reverse_lazy('phdapplications:rev_update_pi', kwargs = {'pk' : app.pk}),      
                      'rc_url' : reverse_lazy('phdapplications:rev_list_letters', kwargs = {'pk' : app.pk}),                                            
                      'next' : request.path,
                      'back_url' : back_url,
                  })

@login_required
@user_passes_test(is_staff_member)
def rev_apply_extra_info(request, pk):
   
    template_name = 'phdapplications/reviewer_app_extra.html'
    staff_member = get_object_or_404(StaffMember, user=request.user)
    application = get_object_or_404(Application, call__reviewers = staff_member, pk = pk)
    back_url = request.GET.get(
                'next',
                reverse_lazy('phdapplications:rev_dashboard')
                )

    tables = [
        Table(
            fields = ['year','get_type_display','department'],
            table_title = _('Πτυχία'),
            headers = {
                'year' : _('Έτος'),
                'get_type_display' : _('Τύπος'),
                'department' : _('Τμήμα'),                
            },
            table_id = 'degrees',
            update_url = 'phdapplications:rev_update_degree',
            create_button = False,
            objects = Degree.objects.filter(application = application),
            next = request.path,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility',
        ),
        Table(
            fields = ['start_date.year','title','company'],
            table_title = _('Εργασιακή Εμπειρία'),
            headers = {
                'start_date.year' : _('Έτος Έναρξης'),
                'title' : _('Τίτλος'),
                'company' : _('Φορέας'),
            },
            table_id = 'workexp',
            update_url = 'phdapplications:rev_update_workexp',
            create_button = False,
            objects = WorkExperience.objects.filter(application = application),
            next = request.path,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility',
        ),
        Table(
            fields = ['year','title','journal_title'],
            table_title = _('Δημοσιεύσεις σε Περιοδικά'),
            headers = {
                'year' : _('Έτος'),
                'title' : _('Τίτλος'),
                'journal_title' : _('Περιοδικό'),
            },
            table_id = 'journals',
            update_url = 'phdapplications:rev_update_journal',
            create_button = False,
            objects = JournalPublication.objects.filter(application = application),
            next = request.path,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility',
        ),
        Table(
            fields = ['year','title','conference_title'],
            table_title = _('Δημοσιεύσεις σε Συνέδρια'),
            headers = {
                'year' : _('Έτος'),
                'title' : _('Τίτλος'),
                'conference_title' : _('Συνέδριο'),
            },
            table_id = 'conferences',
            update_url = 'phdapplications:rev_update_conference',
            create_button = False,
            objects = ConferencePublication.objects.filter(application = application),
            next = request.path,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility',            
        ),
    ]
    context = table_context(tables)
    context['application'] = application
    context['back_url'] = back_url
    
    return render(request, template_name, context=context)

def rev_list_letters(request, pk):
    template_name = 'phdapplications/reviewer_app_rc.html'
    staff_member = get_object_or_404(StaffMember, user=request.user)
    application = get_object_or_404(Application, call__reviewers = staff_member, pk = pk)
    back_url = request.GET.get(
                'next',
                reverse_lazy('phdapplications:rev_dashboard')
                )

    tables = [
        Table(
            fields = ['given_name', 'surname', 'institution', 'submitted_date'],
            table_title = _('Συστατικές Επιστολές'),
            headers = {
                'given_name' : _('Όνομα'),
                'surname' : _('Επώνυμο'),
                'institution' : _('Φορέας'),
                'submitted_date' : _('Ημερομηνία Υποβολής'),
            },
            table_id = 'letters',
            update_url = 'phdapplications:rev_update_letter',
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility',
            create_button = False,
            objects = ReferenceLetter.objects.filter(application = application),
            next = request.path,
        )        
    ]
    context = table_context(tables)
    context['back_url'] = back_url
    return render(request, template_name, context=context)

class ReviewerView(GenericUpdateView):

    def get_object(self):
        object = super().get_object()
        user = self.request.user
        staff_member = get_object_or_404(StaffMember, user=user)
        
        if hasattr(object, 'application'):
            call = object.application.call
        
        elif hasattr(object, 'call'):
            call = object.call
        
        if  staff_member not in call.reviewers.all():
            raise PermissionDenied
        
        return object
    
class rev_view_degree(ReviewerView):
    model = Degree
    form_class = forms.ReviewerDegreeForm 
    headline = _('Στοιχεία τίτλου σπουδών')

class rev_view_journal(ReviewerView):
    model = JournalPublication
    form_class = forms.ReviewerJournalForm
    headline = _('Στοιχεία δημοσίευσης')

class rev_view_conference(ReviewerView):
    model = ConferencePublication
    form_class = forms.ReviewerConferenceForm
    headline = _('Στοιχεία δημοσίευσης')

class rev_view_experience(ReviewerView):
    model = WorkExperience
    form_class = forms.ReviewerExperienceForm
    headline = _('Στοιχεία εργασιακής εμπειρίας')

class rev_view_letter(ReviewerView):
    model = ReferenceLetter
    form_class = forms.ReviewerLetterForm
    headline = _('Συστατική Επιστολή')

class rev_application_main(ReviewerView):
    
    model = Application
    form_class = forms.ReviewerApplicationForm
    template_name = 'phdapplications/rev_application_main.html'
    headline = ('Κύριο σώμα της αίτησης')

class rev_view_pi(ReviewerView):
    model = AppPersonalInfo
    form_class = forms.ReviewerPIFrom
    headline = _('Προσωπικά Στοιχεία')

    def get_object(self):
        staff_member = get_object_or_404(StaffMember, user = self.request.user)
        application = get_object_or_404(Application, pk = self.kwargs['pk'], call__reviewers = staff_member)
        return application.pi  

@login_required
@user_passes_test(is_doctoral_secreteriat)
def sec_call_list(request):
    
    template_name = 'core/multiple_tables.html'
    calls_open = Call.objects.sc_filter(user=request.user).open_for_application()
    calls_expired = Call.objects.sc_filter(user=request.user).expired()
    calls_not_published = Call.objects.not_published()
    calls_not_yet_open = Call.objects.not_open_yet()

    tables = [
        Table( 
            fields = ['title', 'program.department', 'supervisor'],
            table_title = _('Ανοιχτές Προσκλήσεις'),
            headers = {
                'title' : _('Θέμα'),
                'program.department' : _('Τμήμα'),
                'supervisor' : _('Επιβλέπων'),
            },
            table_id = 'open',
            next = request.path,
            create_button = True,
            create_text = _('Νέα πρόσκληση'),
            create_url = 'phdapplications:sec_call_create',          
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility', 
            update_url = 'phdapplications:sec_call_update',
            extra_text = _('Αίτησεις'),
            extra_url = 'phdapplications:sec_list_applications',
            extra_button_icon = 'docs',
            extra_buttons = True,          
            objects = calls_open
        ), 
        Table( 
            fields = ['title', 'program.department', 'supervisor'],
            table_title = _('Προσκλήσεις που έχουν λήξει'),
            headers = {
                'title' : _('Θέμα'),
                'program.department' : _('Τμήμα'),
                'supervisor' : _('Επιβλέπων'),
            },
            table_id = 'closed',
            next = request.path,
            create_button = False,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility', 
            update_url = 'phdapplications:sec_call_update',
            extra_text = _('Αίτησεις'),
            extra_url = 'phdapplications:sec_list_applications',
            extra_button_icon = 'docs',
            extra_buttons = True,          
            objects = calls_expired
        ), 
            Table( 
            fields = ['title', 'program.department', 'supervisor'],
            table_title = _('Προσκλήσεις που δεν έχουν ακόμα ανοίξει'),
            headers = {
                'title' : _('Θέμα'),
                'program.department' : _('Τμήμα'),
                'supervisor' : _('Επιβλέπων'),
            },
            table_id = 'not_yet_open',
            next = request.path,
            create_button = False,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility', 
            update_url = 'phdapplications:sec_call_update',
            extra_text = _('Αίτησεις'),
            extra_url = 'phdapplications:sec_list_applications',
            extra_button_icon = 'docs',
            extra_buttons = True,          
            objects = calls_not_yet_open,
        ), 
            Table( 
            fields = ['title', 'program.department', 'supervisor'],
            table_title = _('Προσκλήσεις που δεν είναι δημοσιευμένες'),
            headers = {
                'title' : _('Θέμα'),
                'program.department' : _('Τμήμα'),
                'supervisor' : _('Επιβλέπων'),
            },
            table_id = 'unpublished',
            next = request.path,
            create_button = False,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility', 
            update_url = 'phdapplications:sec_call_update',
            extra_text = _('Αίτησεις'),
            extra_url = 'phdapplications:sec_list_applications',
            extra_button_icon = 'docs',
            extra_buttons = True,          
            objects = calls_not_published
        ), 
    ]
    context = table_context(tables)
    return render(request, template_name, context = context)

class sec_call_create(ScopedSecCreateView):
    model = Call
    form_class = forms.SecCallForm
    success_url = reverse_lazy('phdapplications:sec_call_list')
    scoped_fields = ['program']

class sec_call_update(ScopedSecUpdateView):
    model = Call
    form_class = forms.SecCallForm
    success_url = reverse_lazy('phdapplications:sec_call_list')
    scoped_fields = ['program']    

@login_required
@user_passes_test(is_doctoral_secreteriat)
def sec_applications(request, pk):
    template_name = 'phdapplications/applications.html'
    call = get_object_or_404(Call.objects.sc_filter(user=request.user), pk = pk)
    applications = Application.objects.filter(call = call).order_by('-date_submitted')    
    tables = [
        Table( 
            fields = ['applicant.given_name', 'applicant.surname', 'date_submitted.date', 'get_status_display'],
            table_title = _('Αιτήσεις'),
            headers = {
              'applicant.given_name' : _('Όνομα'), 
              'applicant.surname' : _('Επώνυμο'),
              'date_submitted.date' : _('Ημερομηνία Υποβολής'),
              'get_status_display': _('Κατάσταση'),
            },
            table_id = 'applications',
            next = request.path,
            create_button = False,
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility', 
            update_url = 'phdapplications:sec_application',
            objects = applications
        ), 
    ]
    context = table_context(tables)
    context['call'] = call
    context['back_url'] = reverse_lazy('phdapplications:sec_call_list')
    return render(request, template_name, context = context)

@login_required
@user_passes_test(is_doctoral_secreteriat)
def sec_application(request, pk):
    template_name = 'phdapplications/sec_app.html'
    app = get_object_or_404(Application, pk = pk)
    app.in_scope_or_403(request.user)
    back_url = request.GET.get(
                'next',
                reverse_lazy('phdapplications:sec_call_list')
                )
    
    return render(request, template_name, 
                  context={
                      'application' : app,
                      'profile' : app.pi,
                      'app_url' : reverse_lazy('phdapplications:sec_application_main', kwargs = {'pk' : app.pk}),
                      'extra_url' : reverse_lazy('phdapplications:sec_application_extra', kwargs = {'pk' : app.pk}),
                      'pi_url' : reverse_lazy('phdapplications:sec_update_pi', kwargs = {'pk' : app.pk}), 
                      'rc_url' : reverse_lazy('phdapplications:sec_list_letters', kwargs = {'pk' : app.pk}), 
                      'delete_url' : reverse_lazy('phdapplications:sec_delete_application', kwargs = {'pk' : app.pk}), 
                      'export_url' : reverse_lazy('phdapplications:export_application_pdf', kwargs = {'pk' : app.pk}),                                        
                      'next' : request.path,
                      'back_url' : back_url,
                  })

@login_required
@user_passes_test(is_doctoral_secreteriat)
def sec_apply_extra_info(request, pk):
   
    template_name = 'phdapplications/reviewer_app_extra.html'
    application = get_object_or_404(Application, pk = pk)
    application.in_scope_or_403(request.user)
    back_url = request.GET.get(
                'next',
                reverse_lazy('phdapplications:sec_call_list')
                )

    tables = [
        Table(
            fields = ['year','get_type_display','department'],
            table_title = _('Πτυχία'),
            headers = {
                'year' : _('Έτος'),
                'get_type_display' : _('Τύπος'),
                'department' : _('Τμήμα'),                
            },
            table_id = 'degrees',
            update_url = 'phdapplications:sec_update_degree',
            create_button = False,
            objects = Degree.objects.filter(application = application),
            next = request.path,
            create_text = 'Νέο Πτυχίο',
        ),
        Table(
            fields = ['start_date.year','title','company'],
            table_title = _('Εργασιακή Εμπειρία'),
            headers = {
                'start_date.year' : _('Έτος Έναρξης'),
                'title' : _('Τίτλος'),
                'company' : _('Φορέας'),
            },
            table_id = 'workexp',
            update_url = 'phdapplications:sec_update_experience',
            create_button = False,
            objects = WorkExperience.objects.filter(application = application),
            next = request.path,
            create_text = 'Νέα Εργασιακή Εμπειρία',
        ),
        Table(
            fields = ['year','title','journal_title'],
            table_title = _('Δημοσιεύσεις σε Περιοδικά'),
            headers = {
                'year' : _('Έτος'),
                'title' : _('Τίτλος'),
                'journal_title' : _('Περιοδικό'),
            },
            table_id = 'journals',
            update_url = 'phdapplications:sec_update_journal',
            create_button = False,
            objects = JournalPublication.objects.filter(application = application),
            next = request.path,
            create_text = 'Νέο Περιοδικό',
        ),
        Table(
            fields = ['year','title','conference_title'],
            table_title = _('Δημοσιεύσεις σε Συνέδρια'),
            headers = {
                'year' : _('Έτος'),
                'title' : _('Τίτλος'),
                'conference_title' : _('Συνέδριο'),
            },
            table_id = 'conferences',
            update_url = 'phdapplications:sec_update_conference',
            create_button = False,
            objects = ConferencePublication.objects.filter(application = application),
            next = request.path,
            create_text = 'Νέο Συνέδριο',
        ),
    ]
    context = table_context(tables)
    context['application'] = application
    context['back_url'] = back_url
    
    return render(request, template_name, context=context)

class SecView(GenericUpdateView):

    def get_object(self):
        object = super().get_object()
        object.in_scope_or_403(self.request.user)
        return object
    
class sec_view_degree(SecView):
    model = Degree
    form_class = forms.SecDegreeForm 
    headline = _('Στοιχεία τίτλου σπουδών')
    delete_url = 'phdapplications:sec_delete_degree'
    
class sec_view_journal(SecView):
    model = JournalPublication
    form_class = forms.SecJournalForm
    headline = _('Στοιχεία δημοσίευσης')
    delete_url = 'phdapplications:sec_delete_journal'
    
class sec_view_conference(SecView):
    model = ConferencePublication
    form_class = forms.SecConferenceForm
    headline = _('Στοιχεία δημοσίευσης')
    delete_url = 'phdapplications:sec_delete_conference'
    
class sec_view_experience(SecView):
    model = WorkExperience
    form_class = forms.SecExperienceForm
    headline = _('Στοιχεία εργασιακής εμπειρίας')
    delete_url = 'phdapplications:sec_delete_experience'
    
class sec_view_letter(SecView):
    model = ReferenceLetter
    form_class = forms.SecLetterForm
    headline = _('Συστατική Επιστολή')
    delete_url = 'phdapplications:sec_delete_letter'    

class sec_application_main(SecView):
    
    model = Application
    form_class = forms.SecApplicationForm
    template_name = 'phdapplications/rev_application_main.html'
    headline = ('Κύριο σώμα της αίτησης')

    def form_valid(self, form):
        new_app = form.instance
        inform_for_rf(new_app)        
        return super().form_valid(form)

class sec_view_pi(SecView):
    model = AppPersonalInfo
    form_class = forms.SecPIFrom
    headline = _('Προσωπικά Στοιχεία')

    def get_object(self):
        application = get_object_or_404(Application, pk = self.kwargs['pk'])
        application.in_scope_or_403(self.request.user)
        return application.pi

def sec_list_letters(request, pk):
    template_name = 'phdapplications/reviewer_app_rc.html'
    application = get_object_or_404(Application, pk = pk)
    back_url = request.GET.get(
                'next',
                reverse_lazy('phdapplications:sec_dashboard')
                )

    tables = [
        Table(
            fields = ['given_name', 'surname', 'institution', 'status'],
            table_title = _('Συστατικές Επιστολές'),
            headers = {
                'given_name' : _('Όνομα'),
                'surname' : _('Επώνυμο'),
                'institurion' : _('Φορέας'),
                'status' : _('Κατάσταση Συστατικής'),
            },
            table_id = 'letters',
            update_url = 'phdapplications:sec_update_letter',
            update_text = _('Λεπτομέρειες'),
            update_button_icon = 'visibility',
            create_button = False,
            objects = ReferenceLetter.objects.filter(application = application),
            next = request.path,
        )        
    ]
    context = table_context(tables)
    context['back_url'] = back_url
    return render(request, template_name, context=context)

class SecDeleteView(GenericDeleteView):

    def can_delete(self, object):
        return object.is_in_scope_of(self.request.user)

class sec_delete_application(SecDeleteView):
    model = Application
    
class sec_delete_degree(SecDeleteView):
    model = Degree

class sec_delete_experience(SecDeleteView):
    model = WorkExperience

class sec_delete_letter(SecDeleteView):
    model = ReferenceLetter

    def can_delete(self, object):
        return super().can_delete(object) and (object.status() == ReferenceContact.NOT_NOTIFIED)

class sec_delete_journal(SecDeleteView):
    model = JournalPublication

class sec_delete_conference(SecDeleteView):
    model = ConferencePublication

@login_required
@user_passes_test(is_doctoral_secreteriat)
def export_application_pdf(request, pk):
    
    application = get_object_or_404(Application, pk=pk)
    application.in_scope_or_403(request.user)
    pdf = build_application_pdf(application)
    filename = f"application_{application.rf}.pdf"
    return FileResponse(pdf, as_attachment = True, filename=filename)
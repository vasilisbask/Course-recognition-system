from django.http import Http404
from .models import Applicant, AppPersonalInfo, Application, Degree, ReferenceContact, WorkExperience, JournalPublication, ConferencePublication, ReferenceLetter
from scopes.models import Secretariat
from core.models import get_latest_or_create, get_or_create_object
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .forms import REQUIRED_APPLICATION_FIELDS, REQUIRED_PI_FIELDS, LABELS
from django.utils.translation import gettext_lazy as _
from .email import INVITATION_REFERENCE_SUBJECT, INVITATION_REFERENCE_BODY, REFERENCE_NUMBER_BODY, REFERENCE_NUMBER_SUBJECT, INFORM_APPLICATION_BODY, INFORM_APPLICATION_TITLE
from django.core.signing import TimestampSigner
from myprofile.utils import get_domain_uri
from mailer.gmail import notify
from django.urls import reverse_lazy
from django.utils import timezone
from export.utils import append_pdf, append_filefield, render_html_to_pdf
from pypdf import PdfWriter
from copy import copy
import io
import os
from django.core.files.base import ContentFile
from django.db.models import FileField, ImageField

User = get_user_model()


def clone_app_instance(instance, new_app):
    new_instance = copy(instance)
    new_instance.pk = None
    new_instance.application = new_app
    for field in new_instance._meta.get_fields():
        if isinstance(field, FileField) or isinstance(field, ImageField):
            file_value = getattr(instance, field.name)
            if file_value:
                filename = os.path.basename(file_value.name)
                file_content = ContentFile(file_value.read())
                new_file_value = getattr(new_instance, field.name)
                new_file_value.save(filename, file_content, save=False)
    new_instance.save()
    return new_instance

def new_application(applicant, call):

    application = Application(applicant = applicant, call = call)
    
    # Check for previous applications 
    previous_apps = Application.objects.filter(applicant = applicant).exclude(status = Application.DRAFT).order_by('-updated_at')
    
    # If previous applications do not exist, just create an empty PI instance and attach it to the new application
    if not previous_apps.exists():
        pi = AppPersonalInfo(applicant = applicant, user=applicant.user, email=applicant.user.email)
        pi.save()
        application.pi = pi
        application.save()
        return application
    
    # If previous applications exist copy PI instance and all related objects
    previous_app = previous_apps.first()

    previous_pi = previous_app.pi
    if previous_pi:
        new_pi = copy(previous_pi)
        new_pi.pk = None
    else:
        new_pi = AppPersonalInfo(applicant = applicant, user=applicant.user, email=applicant.user.email)
    
    new_pi.save()
    
    application.pi = new_pi
    application.save()

    degrees = Degree.objects.filter(application = previous_app)
    for degree in degrees:
        clone_app_instance(degree, application)

    wes = WorkExperience.objects.filter(application = previous_app)
    for we in wes:
        clone_app_instance(we, application)

    journals = JournalPublication.objects.filter(application = previous_app)
    for journal in journals:
        clone_app_instance(journal, application)

    confs = ConferencePublication.objects.filter(application = previous_app)
    for conf in confs:
        clone_app_instance(conf, application)

    return application

# def get_or_create_application(user, call, update_user = None):

#     if isinstance(user, str):
#         user = User.objects.get(username = user)

#     # If a user already has an applicant profile, get that. Otherwise create a new applicant profile for the user
#     applicant = get_latest_or_create(Applicant, update_user = update_user, user = user)

#     existing_applications = Application.objects.filter(applicant = applicant)
#     call_applications = existing_applications.filter(call = call)

#     # Check if the applicant already has an application in thic call. If so get this, otherwise create a new one
#     if call_applications.exists():
#         application = call_applications.first()
#     else:
#         application = Application(applicant = applicant, call = call)
        
#         # Check if the application has an associated PI. If it does not check whether the user 
#         # already has a PI from a previous application and copy that. If he does not create an empty PI

#     if not application.pi:
#         other_call_applications = existing_applications.exclude(call=call).exclude(status=Application.DRAFT).order_by('-updated_at')
#         if other_call_applications.exists():
#             more_recent_app = other_call_applications.first()
#             if more_recent_app.pi:
#                 pi = copy(more_recent_app.pi)
#                 pi.pk = None
#             else:
#                 pi = AppPersonalInfo(applicant = applicant, user = user, email=user.email)
#         else:
#             pi = AppPersonalInfo(applicant = applicant, user = user, email=user.email)
        
#         pi.save(update_user=update_user)            
#         application.pi = pi
#         application.save(update_user=update_user)
#     return application

def get_or_create_application(user, call, update_user = None):

    if isinstance(user, str):
        user = User.objects.get(username = user)

    # If a user already has an applicant profile, get that. Otherwise create a new applicant profile for the user
    applicant = get_latest_or_create(Applicant, update_user = update_user, user = user)

    existing_applications = Application.objects.filter(applicant = applicant)
    call_applications = existing_applications.filter(call = call)

    # Check if the applicant already has an application in thic call. If so get this, otherwise create a new one
    if call_applications.exists():
        application = call_applications.first()
        return application
    
    # If there are no existing applications for this applicant then check if there are applications in other calls and clone
    # staff from there

    application = new_application(applicant, call)    
    return application

def pi_is_complete(profile):
    for field in REQUIRED_PI_FIELDS:
        value = getattr(profile, field)
        if not value:
            return False
    return True

def missing_fields(object, required_fields):
    fields = []
    for field in required_fields:
        value = getattr(object, field)
        if not value:
            fields.append(field)
    return fields

def check_application(application):
    result = {
        'errors' : [],
        'warnings' : [],
        'checked' : []
    }
    pi = application.pi

    # Check main body of application
    app_fields_missing = missing_fields(application, REQUIRED_APPLICATION_FIELDS)
    if len(app_fields_missing) == 0:
        result['checked'].append(
            _('Το κύριο σώμα της αίτησης είναι συμπληρωμένο.')
        )
    else:
        msg = _('Δεν έχετε συμπληρώσει όλα τα απαιτούμενα πεδία στο κύριο μέρος της αίτησης σας: ')
        msg += ", ".join( str(LABELS[f]) for f in app_fields_missing )
        result['errors'].append(msg)


    # Check personal information
    pi_fields_missing = missing_fields(pi, REQUIRED_PI_FIELDS)
    if len(pi_fields_missing) == 0:
        result['checked'].append(
            _('Τα προσωπικά σας στοιχεία είναι συμπληρωμένα.')
        )
    else:
        msg = _('Δεν έχετε συμπληρώσει όλα τα απαιτούμενα πεδία: ')
        msg += ", ".join( str(LABELS[f]) for f in pi_fields_missing )
        result['errors'].append(msg)

    # Check degrees
    degrees = Degree.objects.filter(application = application)
    if not degrees.exists():
        result['warnings'].append(
            _('Δεν έχετε καταχωρήσει καθόλου τίτλους σπουδών')
        )
    else:
        result['checked'].append(
            _('Έχετε καταχωρήσει %(no)s τίτλους σπουδών.') % { 'no' : degrees.count() }
        )

    # Contacts
    contacts = ReferenceContact.objects.filter(application = application)
    if not contacts.exists():
        result['warnings'].append(
            _('Δεν έχετε καταχωρήσει σημεία επαφής για παροχή συστατικής επιστολής. Βεβαιωθείτε ότι δεν απαιτείται από την πρόσκληση.')
        )
    else:
        result['checked'].append(
            _('Έχετε καταχωρήσει %(no)s σημεία επαφής για παροχή συστατικής επιστολής.') % { 'no' : contacts.count() }
        )

    # Work experience
    wes = WorkExperience.objects.filter(application = application)
    if not wes.exists():
        result['warnings'].append(
            _('Δεν έχετε καταχωρήσει καθόλου εργασιακή εμπειρία')
        )
    else:
        result['checked'].append(
            _('Έχετε καταχωρήσει %(no)s εγγραφές στην εργασιακή εμπειρία.') % { 'no' : wes.count() }
        )

    # Journals
    journals = JournalPublication.objects.filter(application = application)
    if not journals.exists():
        result['warnings'].append(
            _('Δεν έχετε καταχωρήσει δημοσιεύσεις σε ερευνητικά περιοδικά')
        )
    else:
        result['checked'].append(
            _('Έχετε καταχωρήσει %(no)s δημοσιεύσεις σε ερευνητικά περιοδικά') % { 'no' : journals.count() }
        )

    # Conferences
    conferences = ConferencePublication.objects.filter(application = application)
    if not conferences.exists():
        result['warnings'].append(
            _('Δεν έχετε καταχωρήσει δημοσιεύσεις σε ερευνητικά συνέδρια')
        )
    else:
        result['checked'].append(
            _('Έχετε καταχωρήσει %(no)s δημοσιεύσεις σε ερευνητικά συνέδρια') % { 'no' : conferences.count() }
        )
    if len(result['errors']) > 0:
        result['errors'].append(
            _('Πατήστε "Επιστροφή" για να τα συμπληρώσετε.')        
        )
    return result

def invite_reviewer(request, ref, application):
    domain = get_domain_uri(request)
    email = ref.email
    invitation = {
        'surname' : ref.surname,
        'name' : ref.given_name,
        'application_id' : application.id,
        'contact_id' : ref.id                    
    }
    applicant = application.applicant
    call = application.call
    signer = TimestampSigner()
    signed_data = signer.sign_object(invitation)
    url = domain + reverse_lazy('phdapplications:reference_letter', kwargs={'token' : signed_data})
    body = INVITATION_REFERENCE_BODY.format(
        url = url,
        name = applicant.given_name,
        surname = applicant.surname,
        department_gr = application.call.program.department.title_gr,
        university_gr = application.call.program.department.school.institution.title_gr,
        department_en = application.call.program.department.title_en,
        university_en = application.call.program.department.school.institution.title_en,        
        call_title_gr = call.title,
        call_title_en = call.title_en,        
    )
    notify.delay(email, INVITATION_REFERENCE_SUBJECT, body)
    ref.invitation_send = True
    ref.invited_on = timezone.now()
    ref.save()

def invite_reviewers(request, application):
    contacts = ReferenceContact.objects.filter(application = application,
                                               invitation_send = False)
    if contacts.exists():
        for contact in contacts:
            invite_reviewer(request, contact, application)

def build_application_pdf(application):
    template = "phdapplications/exports/application_meta.html"
    cover_template = "phdapplications/exports/section_cover.html"
    degree_template = "phdapplications/exports/degree_meta.html"
    experience_template = "phdapplications/exports/experience_meta.html"
    journal_template = "phdapplications/exports/journal_meta.html"
    conference_template = "phdapplications/exports/conference_meta.html"
    reference_template = "phdapplications/exports/reference_letter_meta.html"
    msg_template = "phdapplications/exports/msg.html"
    msg_not_submitted = "Δεν έχει υποβληθεί κάτι σε αυτή την κατηγορία."
    writer = PdfWriter()
    
    context = {
        'application' : application
    }

    pdf = render_html_to_pdf(template,context)
    append_pdf(writer, pdf)

    append_pdf(writer, render_html_to_pdf(cover_template, {'title' : 'Ταυτότητα'} ))    
    append_filefield(writer, application.id_document)
    
    append_pdf(writer, render_html_to_pdf(cover_template, {'title' : 'Βιογραφικό Σημείωμα'} ))    
    append_filefield(writer, application.cv)

    append_pdf(writer, render_html_to_pdf(cover_template, {'title' : 'Υπεύθυνη Δήλωση'} ))    
    append_filefield(writer, application.declaration_not_enlisted)

    append_pdf(writer, render_html_to_pdf(cover_template, {'title' : 'Επιπλέον Τεκμηρίωση'} ))    
    append_filefield(writer, application.additional_doc)

    append_pdf(writer, render_html_to_pdf(cover_template, {'title' : 'Πτυχία'} ))    
    degrees = Degree.objects.filter(application = application)
    if not degrees:
        append_pdf(writer, render_html_to_pdf(msg_template, {'msg': msg_not_submitted} ))
    else:   
        for degree in degrees.all():
            append_pdf(writer, render_html_to_pdf(degree_template, {'degree': degree} ))
            append_filefield(writer, degree.degree)
            append_filefield(writer, degree.transcript_of_records)

    append_pdf(writer, render_html_to_pdf(cover_template, {'title' : 'Συστατικές Επιστολές'} ))    
    refs = ReferenceLetter.objects.filter(application = application)
    if not refs:
        append_pdf(writer, render_html_to_pdf(msg_template, {'msg': msg_not_submitted} ))
    else:
        for ref in refs.all():
            append_pdf(writer, render_html_to_pdf(reference_template, {'ref': ref} ))
            append_filefield(writer, ref.letter)

    append_pdf(writer, render_html_to_pdf(cover_template, {'title' : 'Εργασιακή Εμπειρία'} ))         
    wes = WorkExperience.objects.filter(application = application)
    if not wes:
        append_pdf(writer, render_html_to_pdf(msg_template, {'msg': msg_not_submitted} ))
    else:
        for we in wes.all():
            append_pdf(writer, render_html_to_pdf(experience_template, {'work': we} ))
            append_filefield(writer, we.contract)

    append_pdf(writer, render_html_to_pdf(cover_template, {'title' : 'Δημοσιεύσεις σε Επιστημονικά Περιοδικά'} ))         
    journals = JournalPublication.objects.filter(application = application)
    if not journals:
        append_pdf(writer, render_html_to_pdf(msg_template, {'msg': msg_not_submitted} ))
    else:
        for journal in journals.all():
            append_pdf(writer, render_html_to_pdf(journal_template, {'pub': journal} ))
            append_filefield(writer, journal.pdf)
            
    append_pdf(writer, render_html_to_pdf(cover_template, {'title' : 'Δημοσιεύσεις σε Επιστημονικά Συνέδρια'} ))         
    conferences = ConferencePublication.objects.filter(application = application)
    if not conferences:
        append_pdf(writer, render_html_to_pdf(msg_template, {'msg': msg_not_submitted} ))
    else:
        for conf in conferences.all():
            append_pdf(writer, render_html_to_pdf(conference_template, {'conf': conf} ))
            append_filefield(writer, conf.pdf)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output
    
def inform_for_submission(application):
    old_app = get_object_or_404(Application, pk=application.pk)
    
    if  ( old_app.status == Application.DRAFT ) and (application.status == Application.SUBMITTED):
        secs = Secretariat.objects.filter(programs = application.call.program)
        to_emails = ', '.join([sec.user.email for sec in secs.all() ])
        cc_emails = application.call.supervisor.user.email

        body = INFORM_APPLICATION_BODY.format(
                applicant_name = application.applicant.given_name + ' ' + application.applicant.surname,
                applicant_email = application.applicant.user.email,
                reference_number = application.rf,
                submission_date = application.date_submitted.date(),
                call_title_gr = application.call.title,
                call_title_en = application.call.title_en,
                
        )
        notify.delay(to_emails, INFORM_APPLICATION_TITLE, body, cc=cc_emails)

def inform_for_rf(new_app):
    old_app = get_object_or_404(Application, pk = new_app.pk)
    old_hasnot_rf = (old_app.rf_num == '') or not old_app.rf_num
    new_has_rf = (new_app.rf_num != '') and new_app.rf_num
    
    if old_hasnot_rf and new_has_rf:
       msg = REFERENCE_NUMBER_BODY.format(reference_number = new_app.rf)
       app_email = new_app.applicant.user.email
       secs = Secretariat.objects.filter(programs = new_app.call.program)
       cc_emails = ', '.join([sec.user.email for sec in secs.all() ])
       to_email = new_app.applicant.user.email
       notify.delay(to_email, REFERENCE_NUMBER_SUBJECT, msg, cc = cc_emails)


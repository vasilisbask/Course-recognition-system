from .models import StaffMember, Associate, Student, DoctorateApplicant
from django.urls import reverse_lazy
from django.conf import settings
import re
from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from scopes.utils import get_secreteriat_scope
from curricula.models import StudyProgram, Course
from myprofile.app_landings import APPS
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from scopes.models import Secretariat
from phdstuds.models import PhdThesis
from myprofile.models import StaffMember
from phdapplications.models import Call, Application

User = get_user_model()

def is_internal_user(user):
    return user.email.endswith(settings.INTERNAL_DOMAIN)

def is_external_user(user):
    return not is_internal_user(user)

def is_staff_member(user):
    s = StaffMember.objects.filter(user = user)
    return s.count() == 1

def is_internal_staff_member(user):
    s = StaffMember.objects.filter(user = user, is_internal = True)
    return s.count() == 1

def can_use_theses(user):
    s = StaffMember.objects.filter(user = user)
    if s.exists():        
        return s.first().can_post_theses
    return False

def can_review_phd_apps(user):
    s = StaffMember.objects.filter(user = user)
    if s.exists():
        return s.first().can_review_phd_apps
    return False

def is_external_staff_member(user):
    s = StaffMember.objects.filter(user = user, is_internal = False)
    return s.count() == 1

def is_associate(user):
    s = Associate.objects.filter(user = user)
    return s.count() == 1

def is_secreteriat(user):
    scope = get_secreteriat_scope(user)
    return ( scope['departments'].count() > 0 ) | ( scope['programs'].count() > 0 )

def is_doctoral_secreteriat(user):
    scope = get_secreteriat_scope(user)
    return scope['programs'].filter(type = StudyProgram.DOCTORAL)

def is_course_instructor(user):
    staff_member = StaffMember.objects.filter(user=user)
    if staff_member.exists():
        staff_member = staff_member.first()
        return Course.objects.filter(assigned_to = staff_member).exists()
    return False

def can_apply_for_phd(user):
    s = StaffMember.objects.filter(user = user)
    if s.exists():
        return s.first().can_apply_for_phd
    return True

def supervises_phd(user):
    s = StaffMember.objects.filter(user = user)
    if s.exists():
        staff_member = s.first()
        return PhdThesis.objects.filter(supervisor=staff_member).exists() or PhdThesis.objects.filter(committee=staff_member).exists()
    return False

def is_department_secreteriat(user):
    scope = get_secreteriat_scope(user)
    return scope['departments'].count() > 0

def likely_student_username(user):
    uid = user.username
    return (uid.startswith('it') or uid.startswith('csi') or uid.startswith('ap') ) and not ( (uid =='itsec') or (uid == 'applied') or (uid =='apresvelou' ) ) 

def is_doctoral_student(user):
    return Student.objects.filter(user=user, program__type = StudyProgram.DOCTORAL).exists()

def is_student(user):
    return Student.objects.filter(user=user).exists()

def course_recognition_role(user):
    if not user or not user.is_authenticated:
        return None

    if user.is_superuser:
        return 'admin'

    # The recognition workflow exposes one role per account. A student must
    # not inherit secretariat access from a stale scope row.
    if is_student(user):
        return 'student'

    if is_secreteriat(user):
        return 'secretariat'

    if is_course_instructor(user):
        return 'professor'

    return None

def is_course_recognition_student(user):
    return course_recognition_role(user) == 'student'

def is_course_recognition_secretariat(user):
    return course_recognition_role(user) == 'secretariat'

def is_course_recognition_professor(user):
    return course_recognition_role(user) == 'professor'

def is_course_recognition_admin(user):
    return course_recognition_role(user) == 'admin'

def has_no_doctoral_applicant_profile(user):
    s = DoctorateApplicant.objects.filter(user = user)
    return s.count() == 0

def has_doctoral_applicant_profile(user):
    s = DoctorateApplicant.objects.filter(user = user)
    return s.count() == 1

def get_user_roles(user):

    roles = []

    if isinstance(user, str):
        User = get_user_model()
        user = User.objects.get(username = user)

    if not user or not user.is_authenticated:
        return ['anonymous']

    # --- Secretariat scope (evaluate once) ---
    scope = get_secreteriat_scope(user)

    if scope['departments'].exists():
        return ['department_secretariat']

    if scope['programs'].filter(type=StudyProgram.DOCTORAL).exists():
        return ['doctoral_secretariat']

    if scope['programs'].exists():
        return ['secretariat']

    # --- Staff ---
    staff = StaffMember.objects.filter(user=user).first()
    if staff:
        if staff.is_internal:
            roles = ['internal_staff']
        else:
            roles = ['external_staff']

    # --- Associate ---
    if Associate.objects.filter(user=user).exists():
        roles.append('associate')

    # --- Student ---
    if Student.objects.filter(user=user).exists():
        student = Student.objects.get(user=user)
        if student.program.type == StudyProgram.DOCTORAL:
            roles.append('doctoral_student')
        else:
            roles.append('student')
    
    # --- Simply logged in
    roles.append('logged_in')

    return roles

# def app_urls(user):
#     roles = get_user_roles(user)
#     print(roles)
#     app_dicts = []
#     for role in roles:
#         apps = APPS[role]
#         for app in apps:
#             element = APPS[role][app]
#             print(element)
#             if element not in app_dicts:
#                 app_dicts.append(
#                     element
#                 )

#     return app_dicts

def cond_append_if_not_in(cond, l, lnew):
    if cond:
        for el in lnew:
            if el not in l:
                l.append(el)

def app_urls(user):
    role = course_recognition_role(user)

    if role == 'student':
        return []

    if role == 'secretariat':
        return APPS['course_recognition_secretariat']

    if role == 'professor':
        return []

    if role == 'admin':
        return []

    if is_external_user(user):
        return APPS['change_password']

    return []


def check_password_complexity(p):

    no_special_chars = 0
    for ch in settings.PASSWORD_SPECIAL_CHARS:
        no_special_chars += p.count(ch)

    has_uppercase = re.search(r'[A-Z]', p)
    has_lowercase = re.search(r'[a-z]', p)
    has_digit = re.search(r'\d', p)
    
    return has_digit, has_lowercase, has_uppercase, no_special_chars

def validate_password(password1, password2):

    
    if len(password1) < settings.MIN_LENGTH:
        raise forms.ValidationError(_('Πρέπει να χρησιμοποιήσετε τουλάχιστον %d χαρακτήρες για κωδικό') %settings.MIN_LENGTH)
    
    if password1 != password2:
        raise forms.ValidationError(_('Οι δύο κωδικοί δεν ταιριάζουν!') )
    
    no_special_chars = 0
    for ch in settings.PASSWORD_SPECIAL_CHARS:
        no_special_chars += password1.count(ch)

    has_uppercase = re.search(r'[A-Z]', password1)
    has_lowercase = re.search(r'[a-z]', password1)
    has_digit = re.search(r'\d', password1)
    has_valid_chars = all(
        ch.isupper() or ch.islower() or ch.isdigit() or ch in settings.PASSWORD_SPECIAL_CHARS
        for ch in password1
    )

    msgs = []
    if not has_valid_chars:
        msgs.append( _('Χρησιμοποιήστε μόνο ψηφία από 0 εώς 9, λατινικούς ή τους ειδικούς χαρακτήρες που αναφέρονται παραπάνω.') )

    if not has_digit:
        msgs.append( _('Δεν έχετε χρησιμοποιήσει τουλάχιστον ένα ψηφίο από 0 εώς 9') )
        
    if not has_uppercase:
        msgs.append( _('Δεν έχετε χρησιμοποιήσει τουλάχιστον ένα λατινικό κεφαλαίο γράμμα') )
    
    if not has_lowercase:
        msgs.append( _('Δεν έχετε χρησιμοποιήσει τουλάχιστον ένα λατινικό πεζό γράμμα') )

    if no_special_chars<2:
        msgs.append( _('Δεν έχετε χρησιμοποιήσει τουλάχιστον δύο ειδικούς χαρακτήρες') )
    
    errors = ''
    for msg in msgs:
        errors += """
        <li> <p> %s </p> </li>
        """ % msg

    if errors != '':
        errors = "<ul>" + errors + "</ul>"
        raise forms.ValidationError(mark_safe(errors))
    
def can_download(parts, request_user):

    app_name = parts[0]

    if app_name == 'course_recognition':
        if not request_user.is_authenticated:
            return False

        from django.db.models import Q
        from course_recognition.models import CourseRecognitionRequest

        path = '/'.join(parts)
        recognition_request = CourseRecognitionRequest.objects.filter(
            Q(course_description_file=path)
            | Q(transcript_file=path)
            | Q(degree_file=path)
        ).first()

        if not recognition_request:
            return False

        if request_user.is_superuser or is_course_recognition_secretariat(request_user):
            return True

        if recognition_request.student_id and recognition_request.student.user == request_user:
            return True

        staff_member = StaffMember.objects.filter(user=request_user).first()
        return bool(
            staff_member
            and recognition_request.course_id
            and recognition_request.course.assigned_to.filter(id=staff_member.id).exists()
        )
    
    # Unauthenticated users not allowed
    
    if app_name == 'phdstuds':
    
        file_user = parts[1]
    
        if isinstance(file_user, str):
            file_user = get_object_or_404(User, username=file_user)
    
        if not request_user.is_authenticated:
            return False
        
        student = get_object_or_404(Student, user = file_user, program__type = StudyProgram.DOCTORAL)
        thesis = get_object_or_404(PhdThesis, candidate = student)
        if student.user == request_user:
            return True
        
        elif is_staff_member(request_user):
            staff_member = get_object_or_404(StaffMember, user = request_user)
            if (thesis.supervisor == staff_member) or (staff_member in thesis.committee.all()):       
                return True
        
        else:
            scopes = get_secreteriat_scope(user=request_user)
            if student.program in scopes['programs']:
                return True
            else:
                return False
        
    elif app_name == 'phdapplications':
        domain = parts[1]
        if domain == 'public':
           return True

        if not request_user.is_authenticated:
           return False       

        file_user = parts[2]
        instance_id = parts[3]
        
            
        if domain == 'applicants':
            
            file_users = User.objects.filter(username = file_user)
            if file_users.exists():
                if request_user == file_users.first():
                    return True
            
            
            if is_staff_member(request_user):
                staff_member = get_object_or_404(StaffMember, user = request_user)
                application = get_object_or_404(Application, id = int(instance_id), call__reviewers = staff_member)
                return True


            if is_secreteriat(request_user):
                application = get_object_or_404(Application.objects.sc_filter(user=request_user), id = int(instance_id) )
                if application.is_in_scope_of(request_user):
                    return True
                
            return False
    return True

from django import template
from myprofile.models import StaffMember, Student
from scopes.models import Secretariat
from django.urls import reverse
from myprofile.checks import course_recognition_role, is_secreteriat, is_student, is_staff_member
register = template.Library()

@register.filter(name="is_secretariat")
def test_sec(user):
    return is_secreteriat(user)

@register.filter(name="is_staff_member")
def test_staff_member(user):
    return is_staff_member(user)
    
@register.filter(name="is_student")
def test_student(user):
    return is_student(user)


@register.simple_tag
def role_dashboard_url(user):
    role = course_recognition_role(user)
    if role == 'secretariat':
        return reverse('myprofile:secretariat_dashboard')
    if role == 'student':
        return reverse('myprofile:student_dashboard')
    if role == 'professor':
        return reverse('myprofile:professor_dashboard')
    if role == 'admin':
        return reverse('myprofile:admin_dashboard')
    if not user or not user.is_authenticated:
        return reverse('login')
    return reverse('myprofile:dashboard')

from django import template
from myprofile.models import StaffMember, Student

register = template.Library()

@register.filter(name="as_semester")
def as_semester(semester):
    if semester == 1:
        return 'Χειμερινό'
    elif semester == 2:
        return 'Εαρινό'
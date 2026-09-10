from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy

APPS = {
    'department_secretariat': [
        {
            'title': _('Διπλωματικές'),
            'url': reverse_lazy('theses:sec_list'),
        },
        {
            'title': _('Timesheets'),
            'url': reverse_lazy('timesheets:sec_list'),
        },
        {
            'title': _('Άδειες'),
            'url': reverse_lazy('leaves:sec_list_leaves'),
        },
        {
            'title': _('Έργα'),
            'url': reverse_lazy('projects:sec_list_projects'),
        },
        {
            'title': _('Μαθήματα'),
            'url': reverse_lazy('curricula:list_courses'),
        },
        {
            'title': _('Συνεργάτες'),
            'url': reverse_lazy('myprofile:list_associates'),
        },
        {
            'title': _('Προσωπικό'),
            'url': reverse_lazy('myprofile:list_staff'),
        },
        {
            'title': _('Προκλήσεις Διδακτορικών'),
            'url': reverse_lazy('phdapplications:sec_dashboard'),
        },
        {
            'title': _('Διδακτορικές Διατριβές'),
            'url': reverse_lazy('phdstuds:sec_list_theses'),
        },
    ],
    'secretariat' : [
        {
            'title': _('Διπλωματικές'),
            'url': reverse_lazy('theses:sec_list'),
        },
        {
            'title': _('Μαθήματα'),
            'url': reverse_lazy('curricula:list_courses'),
        },

    ],
    'doctoral_secretariat': [
        {
            'title': _('Προκλήσεις Διδακτορικών'),
            'url': reverse_lazy('phdapplications:sec_dashboard'),
        },
        {
            'title': _('Διδακτορικές Διατριβές'),
            'url': reverse_lazy('phdstuds:sec_list_theses'),
        },
    ],
    'internal_staff': [
        {
            'title': _('Timesheets'),
            'url': reverse_lazy('timesheets:staff_list'),
        },
        {
            'title': _('Άδειες'),
            'url': reverse_lazy('leaves:staff_list_leaves'),
        },
        {
            'title': _('Έργα'),
            'url': reverse_lazy('projects:staff_list_projects'),
        },
        {
            'title': _('Συνεργάτες'),
            'url': reverse_lazy('myprofile:staff_list_associates'),
        },
    ],
    'phdstuds_staff' : [
        {
            'title': _('Διδακτορικές Διατριβές'),
            'url': reverse_lazy('phdstuds:staff_list_theses'),
        },
    ],
    'course_instructor' : [
        {
            'title': _('Μαθήματα'),
            'url': reverse_lazy('curricula:staff_list_course'),
        }
    ],
    'phdapplications_reviewer' : [
        {
            'title': _('Προκλήσεις Διδακτορικών'),
            'url': reverse_lazy('phdapplications:rev_dashboard'),
        },
    ],
    'theses_staff' : [
        {
            'title': _('Διπλωματικές Εργασίες'),
            'url': reverse_lazy('theses:staff_list'),
        },
    ],
    'associate': [],

    'doctoral_student': [
        {
            'title': _('Το διδακτορικό μου'),
            'url': reverse_lazy('phdstuds:stud_overview'),
        },
    ],
    'theses_student': [
        {
            'title': _('Η διπλωματική μου'),
            'url': reverse_lazy('theses:student_dashboard'),
        }
    ],
    'phdapplications_apply' : [
        {
            'title': _('Αίτηση για Διδακτορικό'),
            'url': reverse_lazy('phdapplications:applicant_dashboard'),
        },
    ],
    'course_recognition_student': [
        {
            'title': _('Προσθήκη αίτησης αναγνώρισης'),
            'url': reverse_lazy('course_recognition:student_request_create'),
        },
    ],
    'course_recognition_professor': [
        {
            'title': _('Αιτήσεις αναγνώρισης'),
            'url': reverse_lazy('myprofile:professor_dashboard'),
        },
    ],
    'course_recognition_secretariat': [
        {
            'title': _('Αιτήσεις αναγνώρισης'),
            'url': reverse_lazy('course_recognition:secretariat_requests'),
        },
    ],
    'course_recognition_admin': [],
    'change_password' : [
        {
            'title': _('Διαχείριση συνθηματικού'),
            'url': reverse_lazy('myprofile:password_change'),
        }
    ]
}

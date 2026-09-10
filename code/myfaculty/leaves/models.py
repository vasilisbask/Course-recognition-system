# Create your models here.
from django.db import models
from myprofile.directories import leave_dir
from myprofile.models import StaffMember
from datetime import datetime
from jinja2 import Template
from mailer.gmail import notify
from django.conf import settings
from scopes.models import ScopedQueryDep, ScopedModelDep

CREATION_NOTIFICATION = """
Γειά σας! 

Δημιουργήθηκε νέο αίτημα άδειας που αφορά τον/την:

{{ p.applicant }} 

και αφορά μετάβαση στην πόλη {{ p.city }} από  {{ p.start }} εώς {{ p.end }}

Συνδεθείτε στην πλατφόρμα για περισσότερες λεπτομέρειες

"""

UPDATE_NOTIFICATION = """
Γειά σας! 

Έγινε ενημέρωση του αιτήματος άδειας που αφορά τον/την:

{{ p.applicant }}

και αφορά μετάβαση στην πόλη {{ p.city }} από  {{ p.start }} εώς {{ p.end }}

Συνδεθείτε στην πλατφόρμα για περισσότερες λεπτομέρειες
"""

class LeaveQuery(ScopedQueryDep):
    
    def scope_filter(self, scope):
        return self.filter(applicant__internal_department__in = scope['departments'])
    
class Leave(ScopedModelDep):

    start_date = models.DateField(null=True)
    is_editable = models.BooleanField(null=True, default=True)
    end_date = models.DateField(null=True)
    description = models.TextField(null=True)
    country = models.CharField(max_length = 200, null=True)
    city = models.CharField(max_length = 200, null=True)
    organization = models.CharField(max_length = 200, null=True, blank=True)
    funding_required = models.BooleanField(null=True, blank=True)
    project_title = models.CharField(max_length = 200, null=True, blank=True)
    project_acronym = models.CharField(max_length = 200, null=True, blank=True)
    project_code = models.CharField(max_length = 100, null=True, blank=True)
    travel_expenses = models.FloatField(null=True, blank=True)
    stay_expenses = models.FloatField(null=True, blank=True)
    registration_expenses = models.FloatField(null=True, blank=True)
    ga_document = models.FileField(null=True, blank=True, upload_to=leave_dir)
    applicant = models.ForeignKey(StaffMember, null=True, on_delete=models.SET_NULL)
    updated_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    approved_ga = models.CharField(max_length = 200, null=True, blank=True)    
    objects = LeaveQuery.as_manager()

    def __str__(self):
        return self.applicant.display_name + '(' + self.created_date.strftime('%Y-%m-%d') + ')'
    
    def scope_query(self, scope):
        return scope['departments'].filter(id = self.applicant.internal_department.id).exists()
    
    def notification_dict(self):
        return {
            'city' : self.city,
            'start' : self.start_date,
            'end' : self.end_date,
            'applicant' : self.applicant.display_name
        }
    
    def approval_dict(self):
        return {
            'destinationCity' : self.city,
            'destinationCountry' : self.country,
            'endDate' : self.end_date.strftime('%d/%m/%Y'),
            'startDate' : self.start_date.strftime('%d/%m/%Y'),
            'projectTitle' : self.project_title,
            'description' : self.description,
            'date_now' : self.created_date.strftime('%d/%m/%Y'),
            'applicant' : self.applicant.display_name + ' (' + self.applicant.title +')',
            'projectCode' : self.project_code,
        }
    
    def update_notification(self):
        template = Template(UPDATE_NOTIFICATION)
        return template.render({ 'p' : self.notification_dict() })
    
    def creation_notification(self):
        template = Template(CREATION_NOTIFICATION)
        return template.render({ 'p' : self.notification_dict() })
    
    def notify_creation(self):
        notify.delay(settings.ALWAYS_NOTIFY, 'Νέο αίτημα άδειας', self.creation_notification(), cc=self.applicant.email)

    def notify_update(self):
        notify.delay(self.applicant.email, 'Ενημέρωση αιτήματος άδειας', self.update_notification(), cc=settings.ALWAYS_NOTIFY)

    def save(self, *args, **kwargs):
        new = self.id is None
        if not self.id and not self.created_date:
            self.created_date = datetime.now()

        if self.id and not self.updated_date:
            self.updated_date = datetime.now()

        super().save(*args, **kwargs)

        if new:
            self.notify_creation()
        else:
            self.notify_update()


    
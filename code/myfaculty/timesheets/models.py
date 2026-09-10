from django.db import models
from myprofile.directories import timesheets_dir
from myprofile.models import StaffMember
from datetime import datetime
from jinja2 import Template
from mailer.gmail import notify
from django.conf import settings
from scopes.models import ScopedModelDep, ScopedQueryDep
CREATION_NOTIFICATION = """
Γειά σας! 

Κατατέθηκε ένα νέο timesheet που αφορά τον/την:

{{ p.applicant }}

Για τον μήνα:

{{ p.month }} / {{ p.year }}

Συνδεθείτε στην πλατφόρμα για περισσότερες λεπτομέρειες

"""

UPDATE_NOTIFICATION = """
Γειά σας! 

Υπήρξε μία ενημέρωση των στοιχείων του timesheet που αφορά τον/την:

{{ p.applicant }}

Για τον μήνα:

{{ p.month }} / {{ p.year }}

Συνδεθείτε στην πλατφόρμα για περισσότερες λεπτομέρειες

"""

class TimesheetQuery(ScopedQueryDep):
    
    def scope_filter(self, scope):
        return self.filter(applicant__internal_department__in = scope['departments'])

class Timesheet(ScopedModelDep):

    month = models.IntegerField(default = datetime.now().month, null=True)
    year = models.IntegerField(default = datetime.now().year, null=True )
    unsigned = models.FileField(upload_to=timesheets_dir, null=True)
    signed = models.FileField(upload_to=timesheets_dir, null=True, blank=True)
    applicant = models.ForeignKey(StaffMember, null=True, on_delete=models.SET_NULL )
    updated_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    objects = TimesheetQuery.as_manager()
    
    def __str__(self):
        return self.applicant.display_name + ' ('+ str(self.year) + '/' + str(self.month) + ') '

    def scope_query(self, scope):
        return scope['departments'].filter(id = self.applicant.internal_department.id).exists()

    def save(self, *args, **kwargs):
        new = self.id is  None
        
        if not self.id and not self.created_date:
            self.created_date = datetime.now()

        if self.id and not self.updated_date:
            self.updated_date = datetime.now()

        super().save(*args, **kwargs)

        if new:
            self.notify_creation()
        else:
            self.notify_update()

    def notification_dict(self):
        return {
            'year' : self.year,
            'month' : self.month,
            'applicant' : self.applicant.display_name
        }
    
    def creation_notification(self):
        template = Template(CREATION_NOTIFICATION)
        return template.render({ 'p' : self.notification_dict() })
    
    def update_notification(self):
        template = Template(UPDATE_NOTIFICATION)
        return template.render({ 'p' : self.notification_dict() })
    
    def notify_creation(self):
        notify.delay(settings.DEAN_EMAIL, 'Δημιουργία Νέου Timesheet', self.creation_notification(), cc=self.applicant.email)

    def notify_update(self):
        notify.delay(self.applicant.email, 'Ενημέρωση Timesheet', self.update_notification(), cc=settings.DEAN_EMAIL)




    
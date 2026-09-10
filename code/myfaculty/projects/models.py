from django.db import models
from myprofile.directories import project_dir
from myprofile.models import StaffMember
from datetime import datetime
from jinja2 import Template
from django.forms.models import model_to_dict
from mailer.gmail import notify
from django.conf import settings
from scopes.models import ScopedModelDep, ScopedQueryPrg
from curricula.models import Department

CREATION_NOTIFICATION = """
Γειά σας! 

Δημιουργήθηκε νέο έργο με επιστημονικά υπεύθυνο/η:

{{ p.coordinator }}

Και τίτλο:

{{ p.title }}

Συνδεθείτε στην πλατφόρμα για περισσότερες λεπτομέρειες

"""

UPDATE_NOTIFICATION = """
Γειά σας! 

Υπήρξε μία ενημέρωση των στοιχείων του έργου με τίτλο

{{ p.title }}

με επιστημονικά υπεύθυνο/η:

{{ p.coordinator }}

Συνδεθείτε στην πλατφόρμα για περισσότερες λεπτομέρειες

"""
class ScopedProjectQuery(ScopedQueryPrg):
    def scope_filter(self, scope):
        return self.filter(coordinator__department__in = scope['departments'])
    
class Project(ScopedModelDep):

    is_editable = models.BooleanField(default=True, null=True, blank=True)
    approved = models.BooleanField(default=False, null=True, blank=True)
    submission_approved_ga = models.CharField(max_length=100, null=True, blank=True)
    implementation_approved_ga = models.CharField(max_length=100, null=True, blank=True)
    budget_total = models.FloatField(null=True)
    budget_dep = models.FloatField(null=True)
    call = models.TextField(null=True)
    thematic_areas = models.TextField(null=True)
    title = models.TextField(null=True)
    department_role = models.TextField(null=True)
    department_staff = models.TextField(null=True)
    acronym = models.CharField(max_length=100, null=True, blank=True)
    abstract = models.TextField(null=True)
    partners = models.TextField(null=True)
    funding_date = models.FloatField(null=True, default=100)
    duration = models.FloatField(null=True)
    start = models.DateField(null=True)
    submission_date = models.DateField(null=True, blank=True)
    document_approved_submission = models.FileField(upload_to = project_dir, null=True, blank=True)
    document_approved_implementation = models.FileField(upload_to = project_dir, null=True, blank=True)
    coordinator = models.ForeignKey(StaffMember, null=True, on_delete=models.SET_NULL )
    updated_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)   
    objects = ScopedProjectQuery.as_manager()

    def __str__(self):
        return self.title
    
    def scope_query(self, scope):
        return scope['departments'].filter(id = self.coordinator.department.id).exists()
    
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

    def approval_dict(self):
        return {
            'title' : self.title,
            'acronym' : self.acronym,
            'status' : 'Εγκεκριμένο Έργο' if self.approved else "Υποβολή Πρότασης", 
            'call' : self.call,
            'coordinator' : self.coordinator.display_name,
            'title' : self.coordinator.title,
            'budget' : self.budget_total            
        }
    
    def notification_dict(self):
        return {
            'title' : self.title,
            'coordinator' : self.coordinator.display_name
        }
    
    def creation_notification(self):
        template = Template(CREATION_NOTIFICATION)
        return template.render({ 'p' : self.notification_dict() })
    
    def update_notification(self):
        template = Template(UPDATE_NOTIFICATION)
        return template.render({ 'p' : self.notification_dict() })
    
    def notify_creation(self):
        notify.delay(settings.ALWAYS_NOTIFY, 'Δημιουργία Νέου Έργου', self.creation_notification(), cc=self.coordinator.email)

    def notify_update(self):
        notify.delay(self.coordinator.email, 'Ενημέρωση Έργου', self.update_notification(), cc=settings.ALWAYS_NOTIFY)




    
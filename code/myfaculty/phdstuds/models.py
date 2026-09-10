from django.db import models
from scopes.models import ScopedModelPrg, ScopedQueryPrg
from myprofile.models import StaffMember, Student
from curricula.models import StudyProgram
from django.contrib.auth import get_user_model
from myprofile.directories import phd_dir
from django.utils.translation import gettext_lazy as _
from curricula.models import Course
from rfs.models import ReferenceEntry
from datetime import datetime
from django.utils import timezone

User = get_user_model()
# Create your models here.

class PhdThesisModel(ScopedModelPrg):

    class Meta:
        abstract = True
    
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_updated")

    def save(self, *args, **kwargs):
        now = timezone.now()
        self.updated_at = now
        if not self.id:
            self.created_at = now
        super().save(*args, **kwargs)

class PhdThesisQuery(ScopedQueryPrg):

    def scope_filter(self, scope):
        return self.filter(candidate__program__in = scope['programs'])
    
class PhdThesis(PhdThesisModel):

    COMPLETED = "completed"
    ONGOING = 'ongoing'
    SUSPENDED = 'suspended'
    DELETED = 'deleted'

    STATUS_CHOICES = (
        (COMPLETED, _("Ολοκληρωμένη")),
        (ONGOING, _("Ενεργή")),
        (SUSPENDED, _("Διακοπή φοίτησης")),
        (DELETED, _("Διαγραφή")),
    )

    candidate = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    supervisor = models.ForeignKey(StaffMember, on_delete=models.SET_NULL, null=True, related_name= 'phdthesissup')
    committee = models.ManyToManyField(StaffMember, blank=True, related_name='phdthesiscom')
    subject_gr = models.CharField(max_length = 400, null=True)
    subject_en = models.CharField(max_length = 400, null=True)
    inscription_date = models.DateField(null=True, blank=True)
    inscription_year = models.BigIntegerField(null=True)
    inscription_ga = models.CharField(max_length = 400, null=True)
    notes = models.TextField(null=True, blank=True)
    abstract_gr = models.TextField(null=True, blank=True)
    abstract_en = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, null=True, default=ONGOING)
    objects = PhdThesisQuery.as_manager()
    graduation_date = models.DateField(null=True, blank=True)
    graduation_ga = models.CharField(max_length = 400, null=True, blank=True)
    
    def scope_query(self, scope):
        return scope['programs'].filter(id = self.candidate.program.id).exists()

    def __str__(self):
        return f"{self.subject_gr} - {self.candidate.display_name}"
   
class ThesisScopedQuery(ScopedQueryPrg):
    def scope_filter(self, scope):
        return self.filter(thesis__candidate__program__in = scope['programs'])

class ThesisScopedModel(PhdThesisModel):
    
    class Meta:
        abstract = True

    objects = ThesisScopedQuery.as_manager()
    thesis = models.ForeignKey(PhdThesis, on_delete=models.SET_NULL, null=True)
    
    def scope_query(self, scope):
        return scope['programs'].filter(id = self.thesis.candidate.program.id)
    
class JournalPublication(ThesisScopedModel):
    thesis = models.ForeignKey(PhdThesis, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, null=True)
    journal_title = models.CharField(max_length=255, null=True)
    authors = models.TextField(null=True)
    publisher = models.CharField(max_length=255, null=True)
    issue = models.CharField(max_length=255, null=True)
    volume = models.CharField(max_length=255, null=True)
    pages = models.CharField(max_length=255, null=True)
    year = models.PositiveIntegerField(null=True)
    link = models.URLField(null=True, blank=True)
    doi = models.CharField(null=True, blank=True, max_length=255)
    pdf = models.FileField(upload_to = phd_dir, null=True)
    has_supervisor = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.journal_title})"

class ConferencePublication(ThesisScopedModel):
    title = models.CharField(max_length=500)
    authors = models.TextField()
    conference_title = models.CharField(max_length=255)
    year = models.PositiveIntegerField(null=True)
    link = models.URLField(null=True, blank=True)
    doi = models.CharField(null=True, blank=True, max_length=255)
    pdf = models.FileField(upload_to = phd_dir, null=True)
    venue = models.TextField(null=True)
    has_supervisor = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.conference_title}"

class TaskModel(ThesisScopedModel):
    notes = models.TextField(null=True, blank=True)
    faculty = models.ForeignKey(StaffMember, on_delete=models.SET_NULL, null=True)

    class Meta:
        abstract = True

class TeachingTask(TaskModel):
    LAB = 'lab'
    THEORY = 'theory'
    OTHER = 'other'
    TASK_TYPES = (
        (LAB, _("Διαλέξεις θεωρίας")),
        (THEORY, _("Εργαστηριακά μαθήματα")),
        (OTHER, _("Άλλο")),        
    )
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    course_name = models.CharField(max_length=255, null=True, blank=True)
    hours_per_week = models.FloatField(null=True, blank=True)
    no_weeks = models.FloatField(null=True, blank=True)
    type = models.CharField(null=True, choices=TASK_TYPES)
    year = models.PositiveIntegerField(null=True)
    under_contract = models.BooleanField(null=True, blank=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

class ExamSupervision(TaskModel):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    exam_date = models.DateField(null=True)
    
class AdministrativeTask(TaskModel):
    title = models.CharField(max_length=300, null=True)
    total_hours = models.PositiveIntegerField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

class ThesisProgress(ThesisScopedModel):
    thesis = models.ForeignKey(PhdThesis, null=True, blank=True, on_delete=models.SET_NULL)
    rfs = models.ForeignKey(ReferenceEntry, null=True, blank=True, on_delete=models.SET_NULL)
    pdf = models.FileField(upload_to = phd_dir, null=True)
    year = models.PositiveIntegerField(null=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s %d' %(self.thesis, self.year)
    
class Recommendation(ThesisScopedModel):
    SATISFACTORY = 'satisfactory'
    MARGINAL = 'marginal'
    UNSATISFACTORY = 'unsatisfactory'
    DECISION_CHOICES = (
        (SATISFACTORY, _("Ικανοποιητική")),
        (MARGINAL, _("Οριακά Ικανοποιητική")),
        (UNSATISFACTORY, _("Ανεπαρκής - Διαγραφή")),        
    )
    thesis = models.ForeignKey(PhdThesis, null=True, on_delete=models.SET_NULL)
    rfs = models.ForeignKey(ReferenceEntry, null=True, blank=True, on_delete=models.SET_NULL)
    year = models.PositiveIntegerField(null=True)
    notes = models.TextField(null=True, blank=True)
    recommendation = models.CharField(null=True, max_length = 20, choices=DECISION_CHOICES)
    recommender = models.ForeignKey(StaffMember, null=True, blank=True, on_delete=models.SET_NULL)
    supporting_document = models.FileField(upload_to = phd_dir, null=True, blank=True)

    def __str__(self):
        return '%s %d' %(self.thesis, self.year)
    

    



 


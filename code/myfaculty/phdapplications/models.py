from django.db import models
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from myprofile.directories import phdapp_dir, phdapp_public_dir, phdapp_ref_dir
from datetime import datetime
from myprofile.models import StaffMember
from datetime import datetime, date
from django.utils.translation import gettext_lazy as _
from curricula.models import StudyProgram
from scopes.models import ScopedQueryPrg, ScopedModelPrg
from rfs.models import ReferenceEntry
from core.models import TrackedScopedProgramModel

# Create your models here.
DATE_HELP_TEXT = _('Χρησιμοποιείστε την μορφή DD/MM/YYYY, π.χ. 28/2/2020')
END_HELP_TEXT = _('Χρησιμοποιείστε την μορφή DD/MM/YYYY, π.χ. 28/2/2020. Αν ακόμα απασχολήστε συμπληρώστε την τωρινή ημερομηνία.')

class CallScopedQuery(ScopedQueryPrg):

    def open_for_application(self):
        now = date.today()
        return self.filter(published = True, from_date__lte = now, deadline__gte = now).order_by('from_date')
    
    def expired(self):
        now = date.today()
        return self.filter(published = True, deadline__lt = now).order_by('from_date')
    
    def not_open_yet(self):
        now = date.today()
        return self.filter(published = True, from_date__gt = now).order_by('from_date')
    
    def not_published(self):
        return self.filter(published = False).order_by('from_date')

class Call(TrackedScopedProgramModel):    
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, null=True)    
    description = models.TextField(blank=True, null=True, help_text=_('Περιγραφή της πρόσκλησης'))
    from_date = models.DateField(help_text = DATE_HELP_TEXT)
    deadline = models.DateField(help_text = DATE_HELP_TEXT)
    supervisor = models.ForeignKey('myprofile.StaffMember', on_delete=models.PROTECT, related_name='supervised_cycles')
    reviewers = models.ManyToManyField('myprofile.StaffMember')
    invitation_document = models.FileField(
        upload_to=phdapp_public_dir, 
        blank=True, 
        null=True,
        help_text=_('Επίσημο έγγραφο πρόσκλησης')
    )
    published = models.BooleanField(default=True, blank=True)
    objects = CallScopedQuery.as_manager()
    program = models.ForeignKey(StudyProgram, on_delete=models.SET_NULL, null=True)

    def is_open_for_application(self):
        today = date.today()
        return (self.published) and (today >= self.from_date) and (today <= self.deadline)
     
    def __str__(self):
        return self.title           

class ApplicantQuery(ScopedQueryPrg):

    def scope_filter(self, scope):
        return self.filter(
            application__call__program__in = scope['programs']
        )
    
class Applicant(TrackedScopedProgramModel):
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    surname = models.CharField(max_length=200, null=True)
    given_name = models.CharField(max_length=200, null=True)        
    objects = ApplicantQuery.as_manager()
    
    def save(self, *args, **kwargs):
        if self.user:
            self.given_name = self.user.first_name
            self.surname = self.user.last_name
        super().save(*args, **kwargs)
            
    def __str__(self):
        return f"{self.user.username}"      
    
class AppPersonalInfo(TrackedScopedProgramModel):

    GENDER_MALE = "M"
    GENDER_FEMALE = "F"
    GENDER_OTHER = "O"

    GENDER_CHOICES = (
        (GENDER_MALE, _("Άρρεν")),
        (GENDER_FEMALE, _("Θηλυ")),
        (GENDER_OTHER, _("Άλλο")),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    applicant = models.ForeignKey(Applicant, on_delete=models.SET_NULL, blank=True, null=True)
    given_name = models.CharField(max_length=200, null=True)
    surname = models.CharField(max_length=200, null=True)

    email = models.EmailField(null=True)    
    secondary_email = models.EmailField(null=True, blank=True)    
    fathers_name = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    tin = models.CharField(max_length=50, null=True, blank=True)
    ssn = models.CharField(max_length=50, null=True,blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)

    home_address_street = models.CharField(max_length=70, null=True, blank=True)
    home_address_no = models.IntegerField(null=True, blank=True)
    home_address_po_box = models.CharField(max_length=30, null=True, blank=True)
    home_address_city = models.CharField(max_length=70, null=True, blank=True)
    home_address_country = models.CharField(max_length=70, null=True, default = 'Ελλάδα', blank=True)
    mobile_phone = models.CharField(max_length=30,blank=True, null=True)    
    home_phone = models.CharField(max_length=30,blank=True, null=True)

    work_address_street = models.CharField(max_length=70, null=True, default = 'Ομήρου')
    work_address_no = models.CharField(max_length=10,null=True, default='9')    
    work_address_po_box = models.CharField(max_length=30, null=True, default = '17778')
    work_address_city = models.CharField(max_length=70, null=True, default = 'Αθήνα')
    work_address_country = models.CharField(max_length=70, null=True, default = 'Ελλάδα')
    work_phone = models.CharField(max_length=20,blank=True, null=True)
    pic = models.ImageField(null=True, blank=True)

    def applicant_can_delete(self):
        return False
    
class ApplicationQuery(ScopedQueryPrg):

    def scope_filter(self, scope):
        return self.filter(call__program__in = scope['programs'])

class Application(TrackedScopedProgramModel):
    GENDER_MALE = "M"
    GENDER_FEMALE = "F"
    GENDER_OTHER = "O"

    GENDER_CHOICES = (
        (GENDER_MALE, _("Άρρεν")),
        (GENDER_FEMALE, _("Θηλυ")),
        (GENDER_OTHER, _("Άλλο")),
    )

    ACCEPTED = "accepted"
    FAILED = "failed"
    FINALIZED = "finalized"
    SUBMITTED = "submitted"
    DRAFT = "draft"

    STATUS_CHOICES = (
        (ACCEPTED, _("Επιτυχής")),
        (FAILED, _("Μη επιτυχής")),
        (FINALIZED, _("Οριστικοποιημένη")),
        (SUBMITTED, _("Έχει Υποβληθεί")),
        (DRAFT, _("Προσωρινή"))
    )
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    call = models.ForeignKey(Call, on_delete=models.SET_NULL, null=True)    
    doctoral_plan = models.FileField(upload_to=phdapp_dir, null=True)
    date_submitted = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(null=True, default=DRAFT,choices=STATUS_CHOICES)

    declaration_not_enlisted = models.FileField(null=True, upload_to = phdapp_dir)
    id_document = models.FileField(null=True, upload_to = phdapp_dir)    
    cv = models.FileField(null=True, blank=True, upload_to = phdapp_dir)
    additional_doc = models.FileField(null=True, blank=True, upload_to = phdapp_dir)
    rf = models.ForeignKey(ReferenceEntry, null=True, blank=True, on_delete=models.SET_NULL)
    rf_num = models.CharField(null=True, blank=True)    
    pi = models.ForeignKey(AppPersonalInfo, null=True, on_delete=models.SET_NULL)
    objects = ApplicationQuery.as_manager()

    class Meta:        
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def applicant_can_edit(self):
        call = self.call
        return (self.status in [self.DRAFT,self.SUBMITTED]) and call.is_open_for_application()

    def applicant_can_delete(self):
        return self.status == self.DRAFT

    def applicant_can_submit(self):
        call = self.call
        return (self.status in [self.DRAFT,self.SUBMITTED]) and call.is_open_for_application()
                                               
    def scope_query(self, scope):
        return scope['programs'].filter(id = self.call.program.id).exists()
    
    def __str__(self):
        return f"{self.applicant}"

    def can_edit(self):
        return self.status == self.DRAFT
    
    def save(self, *args, **kwargs):
        if not self.id:
            rf = ReferenceEntry(category = ReferenceEntry.DOCTORATE_APPLICATION)
            rf.save()
            self.rf = rf
        super().save(*args, **kwargs)

    def export_dict(self):
        return {
            'surname' : self.surname,
            'given_name' : self.given_name,
            'fathers_name' : self.fathers_name,
            'birth_date' : self.date_of_birth.strftime('%d/%m/%Y'),
            'city' : self.home_address_city,
            'street' : self.home_address_street,
            'no' : self.home_address_no,
            'postal_code' : self.home_address_po_box,
            'telephone' : self.mobile_phone,
            'email' : self.email,
            'application_date' : self.date_submitted.strftime('%d/%m/%Y'),
            'title' : self.call.title,
            'supervisor' : self.call.supervisor,
            'department' : self.call.program.department.title_gr,
            'school' : self.call.program.department.school.title_gr,
            'rf' : self.rf.display_name
        }

class PhDAppQuery(ScopedQueryPrg):

    def scope_filter(self, scope):        
        return self.filter(application__call__program__in = scope['programs'])
    
class PhDAppModel(TrackedScopedProgramModel):

    class Meta:
        abstract = True
        
    application = models.ForeignKey(Application, related_name="%(app_label)s_%(class)s", on_delete=models.CASCADE, null=True)
    objects = PhDAppQuery.as_manager()

    def save(self, *args, application = None, **kwargs):
        if application:
            self.application = application
        super().save(*args, **kwargs)
    
    def scope_query(self, scope):
        if hasattr(self, 'application'):
            program = self.application.call.program
        elif hasattr(self, 'call'):
            program = self.call.program
        else:
            return False
        return scope['programs'].filter(id = program.id).exists()

    def applicant_can_edit(self):
        call = self.application.call
        return (self.application.status in [Application.DRAFT,Application.SUBMITTED]) and call.is_open_for_application()

    def applicant_can_delete(self):
        return self.applicant_can_edit()

class Degree(PhDAppModel):

    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    DOCTORATE = "doctorate"
    OTHER = "other"

    DEGREE_TYPES = (
        (UNDERGRADUATE, _("Προπτυχιακό")),
        (POSTGRADUATE, _("Μεταπτυχιακό")),
        (DOCTORATE, _("Διδακτορικό")),
        (OTHER, _("Άλλο")),
    )
    
    type = models.CharField(max_length=20, choices=DEGREE_TYPES)
    university = models.CharField(max_length=255)
    school = models.CharField(max_length=255,null=True)
    department = models.CharField(max_length=255,blank=True,null=True)    
    score = models.CharField(max_length=255,null=True)    
    degree = models.FileField(upload_to=phdapp_dir)
    year = models.PositiveIntegerField()
    transcript_of_records = models.FileField(null=True, blank=True, upload_to=phdapp_dir)

    def __str__(self):
        return f"{self.application.applicant.surname} - {self.university} ({self.year})"
    
    def can_review(self, user, application):
        staff_member = get_object_or_404(StaffMember, user = user)
        call = application.call
        return staff_member in call.reviewers


class ReferenceLetter(PhDAppModel):
    email = models.EmailField()
    phone = models.CharField(max_length=30, null=True, blank=True)
    letter = models.FileField(upload_to=phdapp_ref_dir)
    surname = models.CharField(max_length = 255)
    given_name = models.CharField(max_length = 255)
    title = models.CharField(max_length = 255)    
    institution = models.CharField(max_length = 255)
    notes = models.TextField(null=True, blank=True)
    contact = models.ForeignKey('ReferenceContact', on_delete=models.DO_NOTHING, related_name='ref_letter', null=True)
    submitted_date = models.DateField(null=True, blank=True)
    rf = models.ForeignKey(ReferenceEntry, null=True, on_delete=models.SET_NULL)
    def save(self, *args, **kwargs):
        if not self.id:
            rf = ReferenceEntry(category = ReferenceEntry.REFERENCE_LETTER)
            rf.save()
            self.rf = rf
        super().save(*args, **kwargs)

    def scope_query(self, scope):
        program = self.application.call.program
        return scope['programs'].filter(id = program.id).exists()
    
    def __str__(self):
        return f"Reference for {self.application}"

class ReferenceContactQuery(PhDAppQuery):
    def not_yet_submitted(self, application):
        reference_letters_submitted = ReferenceLetter.objects.filter(application = application)
        contacts_submitted = []
        for letters in reference_letters_submitted:
            contacts_submitted.append(letters.contact)

        contacts_invited = application.ref_invited.all()
        contacts_not_submitted = [contact for contact in contacts_invited if contact not in contacts_submitted]
        return contacts_not_submitted
         
class ReferenceContact(PhDAppModel):

    SUBMITTED = _('Υποβλήθηκε')
    PENDING = _('Αναμένεται')
    NOT_NOTIFIED = _('Θα Ειδοποιηθεί Μετά την Υποβολή')
    
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    surname = models.CharField(max_length = 255)
    given_name = models.CharField(max_length = 255)
    title = models.CharField(max_length = 255)    
    institution = models.CharField(max_length = 255)
    objects = ReferenceContactQuery.as_manager()
    invitation_send = models.BooleanField(null=True, default=False)
    invited_on = models.DateField(null=True, blank=True)
    responded_on = models.DateField(null=True, blank=True)
    responded = models.BooleanField(null=True, default=False)    
    def __str__(self):
        return self.given_name + ' ' + self.surname

    def status(self):
        letters = ReferenceLetter.objects.filter(
            application = self.application,
            contact = self
            )
        
        if letters.exists():
            return self.SUBMITTED
        elif self.invitation_send:
            return self.PENDING
        else:
            return self.NOT_NOTIFIED
    
    def applicant_can_delete(self):
        return self.status () == self.NOT_NOTIFIED
    
class JournalPublication(PhDAppModel):
    title = models.CharField(max_length=255)
    journal_title = models.CharField(max_length=255)
    authors = models.TextField()
    publisher = models.CharField(max_length=255)
    volume = models.CharField(max_length=50)
    pages = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    link = models.URLField(null=True, blank=True)
    doi = models.CharField(null=True, blank=True, max_length=255)
    pdf = models.FileField(upload_to=phdapp_dir, null=True)
        
    def __str__(self):
        return f"{self.title} ({self.journal_title})"


class ConferencePublication(PhDAppModel):
    title = models.CharField(max_length=255)
    authors = models.TextField()
    conference_title = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    link = models.URLField(null=True, blank=True)
    doi = models.CharField(null=True, blank=True, max_length=255)
    pdf = models.FileField(upload_to=phdapp_dir, null=True)
    
    def __str__(self):
        return f"{self.title} ({self.conference_title}"
    
class WorkExperience(PhDAppModel):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.DateField(help_text = DATE_HELP_TEXT)
    end_date = models.DateField(help_text = END_HELP_TEXT, null=True)
    duties = models.TextField(null=True)
    contract = models.FileField(upload_to=phdapp_dir)

    def __str__(self):
        return f"{self.title} ({self.application.applicant.surname}"    
    

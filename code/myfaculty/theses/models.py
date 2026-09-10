from django.db import models
from django.db.models import Q
# Create your models here.
from django.db import models
from myprofile.models import StaffMember, Student
from curricula.models import StudyProgram
from datetime import datetime
from jinja2 import Template
from django.conf import settings
import math
from scopes.models import ScopedModelPrg, ScopedQueryPrg

def month_to_semester(month):
    if 3 <= month <= 8:
        semester = 2
    else:
        semester = 1
    return semester

def next_semester(semester, year):
    if semester == 1:
        return 2, year
    elif semester == 2:
        return 1, year+1
            
"""
Add semesters to an existing semester
"""
def add_semesters(semester, year, no_semesters):
    semesters_total = year * 2 + semester - 1 + no_semesters
    return semesters_total % 2 + 1, semesters_total // 2

class ScopedThesisQuery(ScopedQueryPrg):

    def scope_filter(self, scope):
    # secretariat has access to the theses that are either unassigned 
    # and offered_in the program or are assigned to a student in the program
        assigned_to_program = self.filter(assigned_to__program__in = scope['programs'])
        unassigned_offered = self.filter(assigned_to__isnull = True, offered_in__in = scope['programs'])
        
        return assigned_to_program | unassigned_offered
    
class Thesis(ScopedModelPrg):

    DESIGN_SCIENCE = 'Σχεδίαση και Υλοποίηση Συστήματος'
    TECHNOLOGY_ASSESSMENT = 'Αξιολόγηση Τεχνολογίας'
    LITERATURE_REVIEW = 'Βιβλιογραφική Ανασκόπηση'

    TYPE_CHOICES = {
        DESIGN_SCIENCE : DESIGN_SCIENCE,
        TECHNOLOGY_ASSESSMENT : TECHNOLOGY_ASSESSMENT,
        LITERATURE_REVIEW : LITERATURE_REVIEW
    }

    FIELDS_TO_CLEAR = ["assigned_to", "assignment_ga", "assignment_date", 
                       "assigned_program", "official_date", "semester_assigned", 
                       "year_assigned", "declared_date", "declared", 
                       "extension_requested", "extension_requested_date", 
                       "extension_granted", "extension_granted_date", 
                       "extension_granted_ga", "semester_due", "year_due", 
                       "notes", "grade_sup", "grade_member1", "grade_member2", 
                       "grade_avg", "report", "report_created", "document", 
                       "document_created"]

    supervisor = models.ForeignKey(StaffMember, null=True, on_delete=models.SET_NULL )
    member1 = models.ForeignKey(StaffMember, null=True, on_delete=models.SET_NULL, related_name='thesis_member1' )
    member2 = models.ForeignKey(StaffMember, null=True, on_delete=models.SET_NULL, related_name='thesis_member2' )
    title_gr = models.CharField(max_length=300, null=True)
    title_en = models.CharField(max_length=300, null=True)
    abstract = models.TextField(null=True)
    offered_in = models.ManyToManyField(StudyProgram,  limit_choices_to={"active": True})    
    updated_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)    
    is_offered = models.BooleanField(null=True, default=True)
    
    assigned_to = models.ForeignKey(Student, on_delete = models.SET_NULL, null=True, blank=True)
    assignment_ga = models.CharField(max_length=300, null=True, blank=True)
    assignment_date = models.DateTimeField(null=True, blank=True)
    assigned_program = models.ForeignKey(StudyProgram, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_theses',   limit_choices_to={"active": True})
    official_date = models.DateField(null=True, blank=True)
    
    semester_assigned = models.IntegerField(null=True, blank=True)
    year_assigned = models.IntegerField(null=True, blank=True)    
    declared_date = models.DateTimeField(null=True, blank=True)
    declared = models.BooleanField(default=False, null=True, blank=True)

    extension_requested = models.BooleanField(default=False, null=True, blank=True)
    extension_requested_date = models.DateTimeField(null=True, blank=True)
    
    extension_granted = models.BooleanField(default=False, null=True, blank=True)
    extension_granted_date = models.DateTimeField(null=True, blank=True)
    extension_granted_ga = models.CharField(max_length=300, null=True, blank=True)
    
    semester_due = models.IntegerField(null=True, blank=True)
    year_due = models.IntegerField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)
    grade_sup = models.IntegerField(null=True, blank=True)
    grade_member1 = models.IntegerField(null=True, blank=True)
    grade_member2 = models.IntegerField(null=True, blank=True)
    grade_avg = models.IntegerField(null=True, blank=True)
    report = models.FileField(null=True, blank=True)
    report_created = models.DateTimeField(null=True, blank=True)    
    document = models.FileField(null=True, blank=True)
    document_created = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=200, blank=True, choices=TYPE_CHOICES, null=True)
    objects = ScopedThesisQuery.as_manager()

    def __str__(self):
        return self.title_gr + ' ('+ self.supervisor.display_name + ') '
    
    def scope_query(self, scope):
        programs = scope["programs"]

        return programs.filter(
            Q(id = self.assigned_to.program_id)
            if self.assigned_to_id
            else Q(id__in = self.offered_in.values_list("id", flat=True))
        ).exists()
    
    def clear_field(self, field_name):
        field = self._meta.get_field(field_name)
        if field.default is models.NOT_PROVIDED:
            setattr(self, field_name, None) 
        else:
            setattr(self, field_name, field.default)

    def clear_assignment(self):
        for field_name in self.FIELDS_TO_CLEAR:
            self.clear_field(field_name)
        

    def calc_timetable(self):
        month = self.official_date.month
        year = self.official_date.year        
        semester = month_to_semester(month)

        self.year_assigned = year
        self.semester_assigned = semester

        no_semesters_due = self.assigned_program.thesis_semesters
        if self.extension_granted:
            no_semesters_due += 1

        self.semester_due, self.year_due = add_semesters(self.semester_assigned, self.year_assigned, no_semesters_due)

        # if self.extension_granted:
        #     if semester == 2:
        #         self.semester_due = 1
        #         self.year_due = self.year_due + 2
        #     elif semester == 1:
        #         self.semester_due = 2
        #         self.year_due = year + 1
        # else:
        #     self.year_due = year + 1
        #     self.semester_due = semester
            

    def can_ask_extension(self):
        now = datetime.now()
        current_semester = month_to_semester(now.month)
        current_year = now.year
        return (current_year == self.year_due) and (current_semester == self.semester_due) and (self.extension_requested == False)

    def save(self, *args, **kwargs):
        
        if not self.id and not self.created_date:
            self.created_date = datetime.now()

        if self.id:
            self.updated_date = datetime.now()
    
        if self.grade_member1 and self.grade_member2 and self.grade_sup:
            self.grade_avg = round( 1/3 * (self.grade_member1 + self.grade_member2 + self.grade_sup) )

        if self.assigned_to:
            program = self.assigned_to.program
            self.assigned_program = program
            if self.official_date:
                self.calc_timetable()
            
        super().save(*args, **kwargs)

def thesis_to_dict(obj):
    d = {
    'Επιβλέπων': obj.supervisor.display_name,
    '2ο μέλος': obj.member1.display_name,
    '3ο μέλος': obj.member2.display_name,
    'Τίτλος (ΕΛ)': obj.title_gr,
    'Τίτλος (EN)': obj.title_en,
    'Περίληψη': obj.abstract,
    'Ημερομηνία τελευταίας ανανέωσης': obj.updated_date,
    'Ημερομηνία δημιουργίας': obj.created_date,
    'Προσφέρεται': obj.is_offered,
    'Τύπος πτυχιακής' : obj.type,

    'Συνέλευση ανάθεσης': obj.assignment_ga,
    'Ημερομηνία ανάθεσης από τον επιβλέποντα': obj.official_date,    
    'Ημερομηνία επίσημης ανάθεσης': obj.official_date,
    'Εξάμηνο ανάθεσης': obj.semester_assigned,
    'Έτος ανάθεσης': obj.year_assigned,
    'Έχει δηλωθεί' : obj.declared,
    'Ημερομηνία δήλωσης': obj.declared_date,
    
    'Αίτημα παράτασης' : obj.extension_requested,
    'Ημερομηνία αιτήματος παράτασης' : obj.extension_requested_date,
    'Έγκριση αιτήματος παράτασης' : obj.extension_granted_date,
    'Ημερομηνία εξέτασης αιτήματος παράτασης' : obj.extension_granted_date,
    
    'Σημείωσεις': obj.notes,
    'Βαθμός επιβλέποντος': obj.grade_sup,
    'Βαθμός 2ου μέλους': obj.grade_member1,
    'Βαθμός 3ου μέλους': obj.grade_member2,
    'Μέσος όρος': obj.grade_avg
    }

    if obj.assigned_to:
        d['Ανάθεση'] = obj.assigned_to.display_name        
    else:
        d['Ανάθεση'] = ''

    if obj.assigned_program:
        d['Πρόγραμμα σπουδών ανάθεσης'] = obj.assigned_program.title_gr        
    else:
        d['Πρόγραμμα σπουδών ανάθεσης'] = ''

    if (obj.report != '') and obj.report:
        d['Έχει υποβληθεί αναφορά'] = True
    else:
        d['Έχει υποβληθεί αναφορά'] = False

    if (obj.document != '') and obj.document:
        d['Έχει υποβληθεί το κείμενο'] = True
    else:
        d['Έχει υποβληθεί το κείμενο'] = False

    return d

def thesis_filters(program, user, status):

    now = datetime.now()
    year = now.year
    month = now.month
    semester = month_to_semester(month)
    
    if status == 'all':
        status_text = 'Όλες'
        theses = Thesis.objects.sc_filter(Q(assigned_to__program = program) | Q(offered_in = program, assigned_to__isnull=True), user=user ).distinct()
    elif status == 'graded': 
        status_text = 'Βαθμολογημένες'
        theses = Thesis.objects.sc_filter(user=user, assigned_to__program = program, grade_avg__isnull=False).distinct()
    elif status == 'nograde':
        status_text = 'Xωρίς Βαθμολογία'
        theses = Thesis.objects.sc_filter(user=user, assigned_to__program = program, grade_avg__isnull=True).distinct()
    elif status == 'noga':
        status_text = 'Xωρίς Συνέλευση'
        theses = Thesis.objects.sc_filter(user=user, assigned_to__program = program, assignment_ga__isnull=True).distinct()
    elif status == 'expired':
        status_text = 'Εκτός Προθεσμίας'
        theses = Thesis.objects.sc_filter(user=user, assigned_to__program = program, grade_avg__isnull=True, year_due__lt=year, semester_due__lt=semester).distinct()
    elif status == 'expiring':
        status_text = 'Υπό παράδοση'
        theses = Thesis.objects.sc_filter(user=user, assigned_to__program = program, grade_avg__isnull=True, year_due=year, semester_due=semester).distinct()

    return theses, status_text
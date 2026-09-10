from django.db import models
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

from curricula.models import Course
from myprofile.models import StaffMember, Student
from scopes.models import ScopedModelPrg, ScopedQueryPrg


pdf_file_validator = FileExtensionValidator(allowed_extensions=("pdf",))


class CourseRecognitionRequestQuery(ScopedQueryPrg):

    def scope_filter(self, scope):
        # Keep secretariat access limited to the programs included in its scope.
        return self.filter(
            Q(student__program__in=scope["programs"])
            | Q(student__isnull=True, course__program__in=scope["programs"])
        ).distinct()


class CourseRecognitionRequest(ScopedModelPrg):
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

    STATUS_CHOICES = (
        (UNDER_REVIEW, _("Υπό εξέταση")),
        (APPROVED, _("Εγκρίθηκε")),
        (REJECTED, _("Απορρίφθηκε")),
        (WITHDRAWN, _("Αποσύρθηκε / Μη ενεργή")),
    )

    WINTER = "WINTER"
    SPRING = "SPRING"

    SEMESTER_CHOICES = (
        (WINTER, _("Χειμερινό")),
        (SPRING, _("Εαρινό")),
    )

    YEAR_1 = "1"
    YEAR_2 = "2"
    YEAR_3 = "3"
    YEAR_4 = "4"
    YEAR_5 = "5"

    ACADEMIC_YEAR_CHOICES = (
        (YEAR_1, _("1ο")),
        (YEAR_2, _("2ο")),
        (YEAR_3, _("3ο")),
        (YEAR_4, _("4ο")),
        (YEAR_5, _("5ο")),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Φοιτητής"),
        related_name="course_recognition_requests",
    )

    full_name = models.CharField(
        _("Ονοματεπώνυμο"),
        max_length=255,
        blank=True,
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Μάθημα προς αναγνώριση"),
        related_name="recognition_requests",
    )

    title_original_course = models.CharField(
        _("Τίτλος μαθήματος που έχει διδαχθεί στο άλλο πρόγραμμα σπουδών"),
        max_length=255,
    )

    institution = models.CharField(_("Ίδρυμα"), max_length=255)
    school = models.CharField(_("Σχολή"), max_length=255)
    department = models.CharField(_("Τμήμα"), max_length=255, blank=True)
    instructors = models.CharField(_("Διδάσκοντες"), max_length=255)

    academic_year = models.CharField(
        _("Έτος στο οποίο διδάχθηκε"),
        max_length=1,
        choices=ACADEMIC_YEAR_CHOICES,
    )

    academic_semester = models.CharField(
        _("Εξάμηνο στο οποίο διδάχθηκε"),
        max_length=20,
        choices=SEMESTER_CHOICES,
    )

    grade_theory = models.FloatField(_("Βαθμός θεωρητικής εξέτασης"))
    grade_lab = models.FloatField(_("Βαθμός εργαστηριακής εξέτασης"), null=True, blank=True)
    average_grade = models.FloatField(_("Μέσος όρος βαθμολογίας"))
    
    hours_theory = models.FloatField(_("Αριθμός ωρών ανά εβδομάδα - θεωρία"))
    hours_lab = models.FloatField(_("Αριθμός ωρών ανά εβδομάδα - εργαστήριο"), null=True, blank=True)

    description = models.TextField(_("Περιγραφή μαθήματος"))
    url = models.URLField(_("URL μαθήματος"), blank=True)

    course_description_file = models.FileField(
        _("Περιγραφή μαθήματος"),
        upload_to="course_recognition/course_descriptions/",
        validators=(pdf_file_validator,),
    )

    transcript_file = models.FileField(
        _("Αναλυτική βαθμολογία"),
        upload_to="course_recognition/transcripts/",
        validators=(pdf_file_validator,),
    )

    degree_file = models.FileField(
        _("Πτυχίο"),
        upload_to="course_recognition/degrees/",
        validators=(pdf_file_validator,),
    )

    comments = models.TextField(_("Σχόλια φοιτητή"), blank=True)

    protocol_number = models.CharField(
        _("Αριθμός πρωτοκόλλου"),
        max_length=100,
        blank=True,
    )

    status = models.CharField(
        _("Κατάσταση"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=UNDER_REVIEW,
    )

    withdrawn_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Διαγραφή από"),
        related_name="withdrawn_course_recognition_requests",
    )

    withdrawal_reason = models.TextField(_("Αιτιολόγηση διαγραφής"), blank=True)
    withdrawn_at = models.DateTimeField(_("Ημερομηνία διαγραφής"), null=True, blank=True)

    created_at = models.DateTimeField(_("Ημερομηνία δημιουργίας"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Ημερομηνία ενημέρωσης"), auto_now=True)

    objects = CourseRecognitionRequestQuery.as_manager()

    class Meta:
        verbose_name = _("Αίτηση αναγνώρισης μαθήματος")
        verbose_name_plural = _("Αιτήσεις αναγνώρισης μαθημάτων")
        ordering = ("-created_at",)

    def scope_query(self, scope):
        program_id = None

        if self.student_id and self.student.program_id:
            program_id = self.student.program_id
        elif self.course_id and self.course.program_id:
            program_id = self.course.program_id

        if not program_id:
            return False

        return scope["programs"].filter(id=program_id).exists()

    def clean(self):
        super().clean()
        # The selected course must belong to the same department as the student.
        if (
            self.student_id
            and self.course_id
            and self.student.program
            and self.course.program
            and self.student.program.department_id
            and self.course.program.department_id
            and self.student.program.department_id != self.course.program.department_id
        ):
            raise ValidationError(
                {
                    "course": _(
                        "Το μάθημα προς αναγνώριση πρέπει να ανήκει στο τμήμα του φοιτητή."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if self.student_id and not self.full_name:
            self.full_name = self.student.display_name or str(self.student)
        super().save(*args, **kwargs)

    @property
    def student_display_name(self):
        if self.student_id and self.student:
            full_name = " ".join(
                part for part in (self.student.given_name, self.student.surname) if part
            )
            return full_name or self.student.display_name or str(self.student)
        return self.full_name or _("Χωρίς φοιτητή")

    def __str__(self):
        student = self.student_display_name
        course = self.course or _("Χωρίς μάθημα")
        return f"{student} - {course}"


class CourseRecognitionRecommendationQuery(ScopedQueryPrg):

    def scope_filter(self, scope):
        # Recommendations inherit the visibility rules of their request.
        return self.filter(
            Q(request__student__program__in=scope["programs"])
            | Q(request__student__isnull=True, request__course__program__in=scope["programs"])
        ).distinct()


class CourseRecognitionRecommendation(ScopedModelPrg):
    COMPATIBLE = "COMPATIBLE"
    NOT_COMPATIBLE = "NOT_COMPATIBLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"

    COMPATIBILITY_CHOICES = (
        (COMPATIBLE, _("Διδάχθηκε σε συμβατό επίπεδο")),
        (NOT_COMPATIBLE, _("Δεν διδάχθηκε σε συμβατό επίπεδο")),
        (NOT_APPLICABLE, _("Δεν εφαρμόζεται")),
    )

    request = models.OneToOneField(
        CourseRecognitionRequest,
        on_delete=models.CASCADE,
        verbose_name=_("Αίτηση αναγνώρισης"),
        related_name="recommendation",
    )

    professor = models.ForeignKey(
        StaffMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Καθηγητής"),
        related_name="course_recognition_recommendations",
    )

    theoretical_part = models.CharField(
        _("Θεωρητικό μέρος"),
        max_length=20,
        choices=COMPATIBILITY_CHOICES,
    )

    laboratory_part = models.CharField(
        _("Εργαστηριακό μέρος"),
        max_length=20,
        choices=COMPATIBILITY_CHOICES,
        default=NOT_APPLICABLE,
    )

    approval = models.BooleanField(_("Εγκρίνεται"), default=False)

    grade = models.FloatField(_("Βαθμός αναγνώρισης"), null=True, blank=True)

    comments = models.TextField(_("Σχόλια καθηγητή"), blank=True)

    submitted_by_secretariat = models.BooleanField(
        _("Συμπληρώθηκε από γραμματεία"),
        default=False,
    )

    submitted_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Συμπληρώθηκε από χρήστη"),
        related_name="course_recognition_submitted_recommendations",
    )

    created_at = models.DateTimeField(_("Ημερομηνία δημιουργίας"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Ημερομηνία ενημέρωσης"), auto_now=True)

    objects = CourseRecognitionRecommendationQuery.as_manager()

    class Meta:
        verbose_name = _("Εισήγηση αναγνώρισης μαθήματος")
        verbose_name_plural = _("Εισηγήσεις αναγνώρισης μαθημάτων")
        ordering = ("-created_at",)

    def scope_query(self, scope):
        if not self.request_id:
            return False

        return self.request.scope_query(scope)

    def clean(self):
        super().clean()
        # A recognition grade is meaningful only when the recommendation is positive.
        if self.approval and self.grade is None:
            raise ValidationError(
                {
                    "grade": _(
                        "Ο βαθμός αναγνώρισης είναι υποχρεωτικός όταν η εισήγηση εγκρίνεται."
                    )
                }
            )
        if not self.approval and self.grade is not None:
            raise ValidationError(
                {
                    "grade": _(
                        "Ο βαθμός αναγνώρισης συμπληρώνεται μόνο όταν η εισήγηση εγκρίνεται."
                    )
                }
            )

    def __str__(self):
        return f"Εισήγηση για {self.request}"

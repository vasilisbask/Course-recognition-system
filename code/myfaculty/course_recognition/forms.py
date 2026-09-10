from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.utils.translation import get_language, gettext_lazy as _

from dal import autocomplete
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Column, Div, Field, Layout, Row, Submit

from curricula.models import Course
from myprofile.models import StaffMember
from core.widgets import CustomFileInput
from .models import CourseRecognitionRecommendation, CourseRecognitionRequest


REQUEST_FIELDS = (
    "course",
    "title_original_course",
    "institution",
    "school",
    "department",
    "instructors",
    "academic_year",
    "academic_semester",
    "grade_theory",
    "grade_lab",
    "average_grade",
    "hours_theory",
    "hours_lab",
    "description",
    "url",
    "course_description_file",
    "transcript_file",
    "degree_file",
    "comments",
)

REQUEST_LABELS = {
    "full_name": _("Ονοματεπώνυμο"),
    "course": _("Μάθημα προς αναγνώριση"),
    "title_original_course": _("Τίτλος περασμένου μαθήματος"),
    "institution": _("Ίδρυμα"),
    "school": _("Σχολή"),
    "department": _("Τμήμα"),
    "instructors": _("Διδάσκοντες"),
    "academic_year": _("Διδακτικό έτος"),
    "academic_semester": _("Διδακτικό εξάμηνο"),
    "grade_theory": _("Βαθμός θεωρίας"),
    "grade_lab": _("Βαθμός εργαστηρίου"),
    "average_grade": _("Μέσος όρος"),
    "hours_theory": _("Ώρες θεωρίας ανά εβδομάδα"),
    "hours_lab": _("Ώρες εργαστηρίου ανά εβδομάδα"),
    "description": _("Περιγραφή μαθήματος"),
    "url": _("URL μαθήματος"),
    "course_description_file": _("Αρχείο περιγραφής μαθήματος"),
    "transcript_file": _("Αρχείο αναλυτικής βαθμολογίας"),
    "degree_file": _("Αρχείο πτυχίου"),
    "comments": _("Σχόλια αιτούντα"),
}

RECOMMENDATION_LABELS = {
    "theoretical_part": _("Θεωρητικό μέρος"),
    "laboratory_part": _("Εργαστηριακό μέρος"),
    "approval": _("Εγκρίνεται"),
    "grade": _("Βαθμός αναγνώρισης"),
    "comments": _("Σχόλια"),
}


def _configure_numeric_field(field, minimum, maximum, message):
    field.validators.extend(
        [
            MinValueValidator(minimum, message=message),
            MaxValueValidator(maximum, message=message),
        ]
    )
    field.widget.attrs["min"] = minimum
    field.widget.attrs["max"] = maximum
    field.widget.attrs.setdefault("step", "0.1")
    field.widget.attrs["data-range-message"] = message


def _enable_native_required_validation(fields):
    for field in fields.values():
        if field.required and not field.disabled and not field.widget.is_hidden:
            field.widget.attrs["required"] = "required"
            field.widget.attrs["aria-required"] = "true"


def _configure_request_numeric_ranges(fields):
    grade_message = _("Η τιμή πρέπει να είναι από 0 έως 10.")
    hours_message = _("Η τιμή πρέπει να είναι από 1 έως 3.")
    for name in ("grade_theory", "grade_lab", "average_grade"):
        _configure_numeric_field(fields[name], 0, 10, grade_message)
    for name in ("hours_theory", "hours_lab"):
        _configure_numeric_field(fields[name], 1, 3, hours_message)


def _configure_request_instructors_field(field):
    field.help_text = _("Αν υπάρχουν περισσότεροι από ένας διδάσκοντες, χωρίστε τα ονόματα με κόμμα.")
    field.widget = forms.Textarea(
        attrs={
            **field.widget.attrs,
            "class": "form-control",
            "rows": 2,
            "placeholder": _("π.χ. Ιωάννης Παπαδόπουλος, Μαρία Νικολάου"),
        }
    )


def _configure_existing_file_names(fields, instance):
    if not instance:
        return
    for name in ("course_description_file", "transcript_file", "degree_file"):
        existing_file = getattr(instance, name, None)
        if existing_file and getattr(existing_file, "name", ""):
            fields[name].widget.attrs["data-existing-filename"] = existing_file.name.replace("\\", "/").split("/")[-1]


def courses_for_student(student):
    if not student or not student.program_id or not student.semester:
        return Course.objects.none()

    # Students may request recognition only for courses in their own program and semester.
    return Course.objects.filter(
        active=True,
        program=student.program,
        semester=student.semester,
    ).order_by("semester", "title_gr")


class StudentCourseRecognitionRequestForm(forms.ModelForm):
    class Meta:
        model = CourseRecognitionRequest
        fields = REQUEST_FIELDS
        labels = REQUEST_LABELS
        widgets = {
            "course": autocomplete.ModelSelect2(url="course_recognition:student_course_autocomplete"),
            "course_description_file": CustomFileInput(),
            "transcript_file": CustomFileInput(),
            "degree_file": CustomFileInput(),
        }

    def __init__(self, *args, student=None, **kwargs):
        self.student = student
        super().__init__(*args, **kwargs)
        self.fields["course"].required = True
        self.fields["academic_year"].choices = CourseRecognitionRequest.ACADEMIC_YEAR_CHOICES
        self.fields["academic_semester"].choices = CourseRecognitionRequest.SEMESTER_CHOICES
        _configure_existing_file_names(self.fields, self.instance)
        for name in ("course_description_file", "transcript_file", "degree_file"):
            self.fields[name].widget.attrs["accept"] = "application/pdf,.pdf"
        _configure_request_numeric_ranges(self.fields)
        _configure_request_instructors_field(self.fields["instructors"])
        _enable_native_required_validation(self.fields)

        courses_qs = courses_for_student(student)
        self.fields["course"].queryset = courses_qs
        self.fields["course"].error_messages["invalid_choice"] = _(
            "Το μάθημα δεν ανήκει στο πρόγραμμα σπουδών και το εξάμηνο του φοιτητή."
        )
        self.fields["course"].empty_label = None
        if not courses_qs.exists():
            self.fields["course"].help_text = _(
                "Δεν βρέθηκαν μαθήματα για το πρόγραμμα σπουδών και το εξάμηνο του φοιτητή."
            )
            # Disabling the field avoids submitting a request with an invalid empty course.
            self.fields["course"].widget.attrs["disabled"] = "disabled"
            self.fields["course"].widget.attrs["aria-disabled"] = "true"

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_enctype = "multipart/form-data"
        self.helper.layout = Layout(
            HTML(f"<h5>{_('Στοιχεία αίτησης')}</h5>"),
            Row(
                Column(Field("course"), css_class="col-lg-12"),
            ),
            HTML(f"<h5>{_('Στοιχεία περασμένου μαθήματος')}</h5>"),
            Row(
                Column(Field("title_original_course"), css_class="col-lg-12"),
            ),
            Row(
                Column(Field("institution"), css_class="col-lg-4"),
                Column(Field("school"), css_class="col-lg-4"),
                Column(Field("department"), css_class="col-lg-4"),
            ),
            Row(
                Column(Field("instructors"), css_class="col-lg-6"),
                Column(Field("academic_year"), css_class="col-lg-3"),
                Column(Field("academic_semester"), css_class="col-lg-3"),
            ),
            HTML(f"<h5>{_('Βαθμολογία και ώρες')}</h5>"),
            Row(
                Column(Field("grade_theory"), css_class="col-lg-4"),
                Column(Field("grade_lab"), css_class="col-lg-4"),
                Column(Field("average_grade"), css_class="col-lg-4"),
            ),
            Row(
                Column(Field("hours_theory"), css_class="col-lg-6"),
                Column(Field("hours_lab"), css_class="col-lg-6"),
            ),
            HTML(f"<h5>{_('Τεκμηρίωση')}</h5>"),
            Row(
                Column(Field("description"), css_class="col-lg-12"),
            ),
            Row(
                Column(Field("url"), css_class="col-lg-12"),
            ),
            Row(
                Column(Field("course_description_file"), css_class="col-lg-4"),
                Column(Field("transcript_file"), css_class="col-lg-4"),
                Column(Field("degree_file"), css_class="col-lg-4"),
            ),
            Row(
                Column(Field("comments"), css_class="col-lg-12"),
            ),
            Div(Submit("submit", _("Υποβολή"), css_class="btn btn-primary"), css_class="text-end"),
        )

    def clean_course(self):
        course = self.cleaned_data["course"]
        if course not in self.fields["course"].queryset:
            raise forms.ValidationError(_("Το μάθημα δεν ανήκει στο τμήμα του φοιτητή."))
        return course

    def clean(self):
        cleaned_data = super().clean()
        # Keep server-side validation aligned with the autocomplete restrictions.
        course = cleaned_data.get("course")
        if course and self.student and self.student.program_id and course.program_id != self.student.program_id:
            self.add_error("course", _("Το μάθημα δεν ανήκει στο πρόγραμμα σπουδών του φοιτητή."))
        if course and self.student and self.student.semester and int(course.semester) != int(self.student.semester):
            self.add_error("course", _("Το μάθημα δεν ανήκει στο εξάμηνο του φοιτητή."))
        return cleaned_data


class SecretariatProtocolForm(forms.ModelForm):
    class Meta:
        model = CourseRecognitionRequest
        fields = ("protocol_number",)
        labels = {
            "protocol_number": _("Αριθμός πρωτοκόλλου"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        protocol_field = self.fields["protocol_number"]
        protocol_field.required = True
        protocol_message = (
            "The protocol number must be a positive integer."
            if (get_language() or "").startswith("en")
            else _("Ο αριθμός πρωτοκόλλου πρέπει να είναι θετικός ακέραιος αριθμός.")
        )
        protocol_field.widget.attrs.update(
            {
                "inputmode": "numeric",
                "pattern": "[1-9][0-9]*",
                "data-pattern-message": protocol_message,
                "oninput": "this.value = this.value.replace(/\\D/g, '');",
            }
        )
        _enable_native_required_validation(self.fields)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field("protocol_number"),
            Div(Submit("submit", _("Αποθήκευση"), css_class="btn btn-primary"), css_class="text-end"),
        )

    def clean_protocol_number(self):
        protocol_number = self.cleaned_data.get("protocol_number")
        if protocol_number:
            is_english = (get_language() or "").startswith("en")
            protocol_number = protocol_number.strip()
            if not protocol_number.isdigit():
                message = (
                    "The protocol number must be a positive integer."
                    if is_english
                    else _("Ο αριθμός πρωτοκόλλου πρέπει να είναι θετικός ακέραιος αριθμός.")
                )
                raise forms.ValidationError(message)
            if int(protocol_number) <= 0:
                message = (
                    "The protocol number must be greater than zero."
                    if is_english
                    else _("Ο αριθμός πρωτοκόλλου πρέπει να είναι μεγαλύτερος από το μηδέν.")
                )
                raise forms.ValidationError(message)

            # Μοναδικότητα
            qs = CourseRecognitionRequest.objects.filter(protocol_number=protocol_number)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                message = (
                    "This protocol number is already used in another request."
                    if is_english
                    else _("Αυτός ο αριθμός πρωτοκόλλου χρησιμοποιείται ήδη σε άλλη αίτηση.")
                )
                raise forms.ValidationError(message)
        return protocol_number



class CourseInstructorAssignmentForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        label=_("Μάθημα"),
        required=True,
        empty_label=None,
    )
    instructors = forms.ModelChoiceField(
        queryset=StaffMember.objects.none(),
        label=_("Υπεύθυνοι καθηγητές"),
        required=True,
        empty_label=None,
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if (get_language() or "").startswith("en"):
            self.fields["course"].label = "Course"
            self.fields["instructors"].label = "Responsible professor"
        self.fields["course"].widget = autocomplete.ModelSelect2(
            url="course_recognition:secretariat_course_autocomplete",
        )
        self.fields["instructors"].widget = autocomplete.ModelSelect2(
            url="course_recognition:professor_autocomplete",
        )
        courses = Course.objects.filter(active=True)
        if user is not None:
            from scopes.models import Secretariat

            program_ids = Secretariat.objects.filter(user=user).values_list("programs", flat=True)
            courses = courses.filter(program_id__in=program_ids)

        self.fields["course"].queryset = courses.order_by(
            "program__title_gr",
            "semester",
            "title_gr",
        )
        self.fields["instructors"].queryset = StaffMember.objects.filter(user__is_active=True).order_by(
            "surname",
            "given_name",
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        _enable_native_required_validation(self.fields)

        course_id = self.data.get("course") if self.is_bound else self.initial.get("course")
        if course_id:
            try:
                course = self.fields["course"].queryset.get(pk=course_id)
                self.fields["instructors"].initial = course.assigned_to.order_by(
                    "surname",
                    "given_name",
                ).first()
            except Course.DoesNotExist:
                pass

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field("course"),
            Field("instructors"),
            Div(Submit("submit", _("Αποθήκευση"), css_class="btn btn-primary"), css_class="text-end"),
        )

    def save(self):
        course = self.cleaned_data["course"]
        instructor = self.cleaned_data["instructors"]
        if course.assigned_to.filter(pk=instructor.pk).exists():
            return course, instructor, False

        course.assigned_to.add(instructor)
        return course, instructor, True


class CourseInstructorImportForm(forms.Form):
    import_file = forms.FileField(
        label=_("Αρχείο CSV"),
        required=True,
        error_messages={"required": _("Πρέπει να επιλεχθεί κάποιο αρχείο.")},
        widget=forms.FileInput(attrs={"accept": ".csv,text/csv", "class": "form-control"}),
    )

    def clean_import_file(self):
        import_file = self.cleaned_data["import_file"]
        if not import_file.name.lower().endswith(".csv"):
            raise forms.ValidationError(_("Το αρχείο πρέπει να είναι CSV."))
        return import_file


class AdminCourseRecognitionRequestForm(forms.ModelForm):
    class Meta:
        model = CourseRecognitionRequest
        fields = (
            "course",
            "title_original_course",
            "institution",
            "school",
            "department",
            "instructors",
            "academic_year",
            "academic_semester",
            "grade_theory",
            "grade_lab",
            "average_grade",
            "hours_theory",
            "hours_lab",
            "description",
            "url",
            "course_description_file",
            "transcript_file",
            "degree_file",
            "comments",
        )
        labels = REQUEST_LABELS
        widgets = {
            "course": autocomplete.ModelSelect2(url="course_recognition:student_course_autocomplete"),
            "course_description_file": CustomFileInput(),
            "transcript_file": CustomFileInput(),
            "degree_file": CustomFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].required = True
        self.fields["academic_year"].choices = CourseRecognitionRequest.ACADEMIC_YEAR_CHOICES
        self.fields["academic_semester"].choices = CourseRecognitionRequest.SEMESTER_CHOICES
        if self.instance and self.instance.pk:
            self.fields["course"].widget = autocomplete.ModelSelect2(
                url=reverse("course_recognition:admin_course_autocomplete", args=(self.instance.pk,)),
            )
        _configure_existing_file_names(self.fields, self.instance)
        for name in ("course_description_file", "transcript_file", "degree_file"):
            self.fields[name].widget.attrs["accept"] = "application/pdf,.pdf"
        _configure_request_numeric_ranges(self.fields)
        _configure_request_instructors_field(self.fields["instructors"])

        # Filter the course queryset based on the student's program and semester
        student = self.instance.student if self.instance else None
        if student and student.program_id and student.semester:
            courses_qs = Course.objects.filter(
                active=True,
                program=student.program,
                semester=student.semester,
            ).order_by("semester", "title_gr")
            self.fields["course"].queryset = courses_qs
        else:
            self.fields["course"].queryset = Course.objects.all().order_by("program__title_gr", "semester", "title_gr")
        self.fields["course"].empty_label = None

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        _enable_native_required_validation(self.fields)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_enctype = "multipart/form-data"
        self.helper.layout = Layout(
            HTML(f"<h5>{_('Στοιχεία αίτησης')}</h5>"),
            Row(
                Column(Field("course"), css_class="col-lg-12"),
            ),
            HTML(f"<h5>{_('Στοιχεία περασμένου μαθήματος')}</h5>"),
            Row(
                Column(Field("title_original_course"), css_class="col-lg-12"),
            ),
            Row(
                Column(Field("institution"), css_class="col-lg-4"),
                Column(Field("school"), css_class="col-lg-4"),
                Column(Field("department"), css_class="col-lg-4"),
            ),
            Row(
                Column(Field("instructors"), css_class="col-lg-6"),
                Column(Field("academic_year"), css_class="col-lg-3"),
                Column(Field("academic_semester"), css_class="col-lg-3"),
            ),
            HTML(f"<h5>{_('Βαθμολογία και ώρες')}</h5>"),
            Row(
                Column(Field("grade_theory"), css_class="col-lg-4"),
                Column(Field("grade_lab"), css_class="col-lg-4"),
                Column(Field("average_grade"), css_class="col-lg-4"),
            ),
            Row(
                Column(Field("hours_theory"), css_class="col-lg-6"),
                Column(Field("hours_lab"), css_class="col-lg-6"),
            ),
            HTML(f"<h5>{_('Τεκμηρίωση')}</h5>"),
            Field("description"),
            Field("url"),
            Row(
                Column(Field("course_description_file"), css_class="col-lg-4"),
                Column(Field("transcript_file"), css_class="col-lg-4"),
                Column(Field("degree_file"), css_class="col-lg-4"),
            ),
            Field("comments"),
            Div(Submit("submit", _("Αποθήκευση"), css_class="btn btn-primary"), css_class="text-end"),
        )

class RecommendationForm(forms.ModelForm):
    class Meta:
        model = CourseRecognitionRecommendation
        fields = (
            "theoretical_part",
            "laboratory_part",
            "approval",
            "grade",
            "comments",
        )
        labels = RECOMMENDATION_LABELS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["theoretical_part"].choices = [
            (c, label) for c, label in CourseRecognitionRecommendation.COMPATIBILITY_CHOICES
            if c != CourseRecognitionRecommendation.NOT_APPLICABLE
        ]
        _configure_numeric_field(
            self.fields["grade"],
            5,
            10,
            _("Η τιμή πρέπει να είναι από 5 έως 10."),
        )
        _enable_native_required_validation(self.fields)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column(Field("theoretical_part"), css_class="col-lg-6"),
                Column(Field("laboratory_part"), css_class="col-lg-6"),
            ),
            Row(
                Column(Field("approval"), css_class="col-lg-6"),
                Column(Field("grade"), css_class="col-lg-6"),
            ),
            Field("comments"),
            Div(Submit("submit", _("Υποβολή"), css_class="btn btn-primary"), css_class="text-end"),
        )

    def clean(self):
        cleaned_data = super().clean()
        approval = cleaned_data.get("approval")
        grade = cleaned_data.get("grade")
        if approval and grade is None:
            self.add_error(
                "grade",
                _("Ο βαθμός αναγνώρισης είναι υποχρεωτικός όταν η εισήγηση εγκρίνεται."),
            )
        if not approval and grade is not None:
            self.add_error(
                "grade",
                _("Ο βαθμός αναγνώρισης συμπληρώνεται μόνο όταν η εισήγηση εγκρίνεται."),
            )
        return cleaned_data

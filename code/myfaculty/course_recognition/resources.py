import csv
import io

import tablib
from django.db import transaction
from django.db.models import Q
from django.utils.translation import get_language, gettext_lazy as _
from import_export import resources

from curricula.models import Course
from myprofile.models import StaffMember


def course_assignment_exists_message(professor, course):
    is_english = (get_language() or "").startswith("en")
    professor_name = (
        professor.display_name_en if is_english and professor.display_name_en else professor.display_name
    ) or professor.email
    course_title = (
        course.title_en if is_english and course.title_en else course.title_gr
    ) or str(course)

    if is_english:
        return f"Professor {professor_name} is already responsible for course {course_title}."

    return _(
        "Ο καθηγητής %(professor)s είναι ήδη υπεύθυνος στο μάθημα %(course)s."
    ) % {
        "professor": professor_name,
        "course": course_title,
    }


class CourseInstructorAssignmentResource(resources.Resource):
    required_headers = {"course_code", "professor_email"}

    def __init__(self, *, program_ids):
        super().__init__()
        self.program_ids = list(program_ids)

    @classmethod
    def dataset_from_upload(cls, uploaded_file):
        raw = uploaded_file.read()
        # Accept the common encodings used by Greek CSV exports.
        for encoding in ("utf-8-sig", "utf-8", "cp1253"):
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                text = None
        if text is None:
            raise ValueError(_("Το αρχείο CSV δεν μπορεί να διαβαστεί. Χρησιμοποιήστε UTF-8."))

        sample = text[:2048]
        try:
            # The import accepts both semicolon and comma separated CSV files.
            delimiter = csv.Sniffer().sniff(sample, delimiters=";,").delimiter
        except csv.Error:
            delimiter = ";"

        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        if not reader.fieldnames:
            return tablib.Dataset()

        original_headers = reader.fieldnames
        normalized_headers = [header.strip().lower() for header in original_headers]
        dataset = tablib.Dataset(headers=normalized_headers)
        for row in reader:
            dataset.append([row.get(header, "") for header in original_headers])
        return dataset

    def import_assignments(self, dataset):
        errors = self._validate_headers(dataset)
        if errors:
            return 0, 0, errors, []

        # Collect valid assignments first, then save them in one transaction.
        unchanged_count = 0
        unchanged_messages = []
        seen_unchanged_assignments = set()
        assignments = []
        seen_assignments = set()
        rows_seen = 0

        for line_number, row in enumerate(dataset.dict, start=2):
            rows_seen += 1
            course_code = (row.get("course_code") or "").strip()
            professor_email = (row.get("professor_email") or "").strip()
            if not course_code and not professor_email:
                continue
            if not course_code or not professor_email:
                errors.append(_("Συμπληρώστε course_code και professor_email."))
                continue

            course = self._get_course(course_code, line_number, errors)
            if not course:
                continue

            professor = self._get_professor(professor_email, line_number, errors)
            if not professor:
                continue

            assignment_key = (course.pk, professor.pk)
            if course.assigned_to.filter(pk=professor.pk).exists() or assignment_key in seen_assignments:
                unchanged_count += 1
                if assignment_key not in seen_unchanged_assignments:
                    unchanged_messages.append(course_assignment_exists_message(professor, course))
                    seen_unchanged_assignments.add(assignment_key)
            else:
                seen_assignments.add(assignment_key)
                assignments.append((course, professor))

        if not rows_seen:
            errors.append(_("Το CSV δεν περιέχει γραμμές για import."))

        with transaction.atomic():
            for course, professor in assignments:
                course.assigned_to.add(professor)

        return len(assignments), unchanged_count, errors, unchanged_messages

    def _validate_headers(self, dataset):
        if not dataset.headers:
            return [_("Το CSV πρέπει να έχει επικεφαλίδες.")]

        missing_headers = self.required_headers - set(dataset.headers)
        if missing_headers:
            return [_("Το CSV πρέπει να έχει στήλες course_code και professor_email.")]

        return []

    def _get_course(self, course_code, line_number, errors):
        # Secretariats can import assignments only for courses in their programs.
        courses = Course.objects.filter(
            Q(code_gr__iexact=course_code) | Q(code_en__iexact=course_code),
            active=True,
            program_id__in=self.program_ids,
        )
        course = courses.first()
        if not course:
            errors.append(
                _("Δεν βρέθηκε μάθημα με κωδικό %(code)s.")
                % {"code": course_code}
            )
            return None
        if courses.count() > 1:
            errors.append(
                _("Ο κωδικός %(code)s αντιστοιχεί σε περισσότερα από ένα μαθήματα.")
                % {"code": course_code}
            )
            return None
        return course

    def _get_professor(self, professor_email, line_number, errors):
        professor = (
            StaffMember.objects
            .filter(Q(email__iexact=professor_email) | Q(user__email__iexact=professor_email), user__is_active=True)
            .order_by("id")
            .first()
        )
        if not professor:
            errors.append(
                _("Δεν βρέθηκε καθηγητής με email %(email)s.")
                % {"email": professor_email}
            )
        return professor

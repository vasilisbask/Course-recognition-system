from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from curricula.models import Department, StudyProgram, Course
from myprofile.checks import can_download, course_recognition_role
from myprofile.models import StaffMember, Student
from scopes.models import Secretariat
from course_recognition.models import CourseRecognitionRequest, CourseRecognitionRecommendation
from course_recognition.forms import (
    CourseInstructorAssignmentForm,
    RecommendationForm,
    SecretariatProtocolForm,
    StudentCourseRecognitionRequestForm,
)
from course_recognition.resources import CourseInstructorAssignmentResource
from course_recognition.views import _professor_queryset, _secretariat_queryset
from myfaculty.auth import CustomAuthBackend

User = get_user_model()

class CourseRecognitionTests(TestCase):
    def setUp(self):
        # Create department
        self.dept = Department.objects.create(
            title_gr="Τμήμα Πληροφορικής",
            title_en="Department of Informatics",
            code_gr="CS",
            code_en="CS"
        )
        # Create study programs
        self.program1 = StudyProgram.objects.create(
            title_gr="Προπτυχιακό Πληροφορικής",
            title_en="Undergraduate CS",
            department=self.dept,
            type=StudyProgram.UNDERGRADUATE
        )
        self.program2 = StudyProgram.objects.create(
            title_gr="Μεταπτυχιακό Πληροφορικής",
            title_en="Postgraduate CS",
            department=self.dept,
            type=StudyProgram.POSTGRADUATE
        )
        
        # Create courses
        self.course1 = Course.objects.create(
            program=self.program1,
            code_gr="CS101",
            code_en="CS101",
            semester=1,
            title_gr="Εισαγωγή στην Πληροφορική",
            title_en="Intro to CS",
            ects_credits=5,
            active=True,
            hours_study=0.0,
            hours_project=0.0,
            hours_lab_prep=0.0
        )
        self.course2 = Course.objects.create(
            program=self.program2,
            code_gr="CS501",
            code_en="CS501",
            semester=1,
            title_gr="Προηγμένη Πληροφορική",
            title_en="Advanced CS",
            ects_credits=5,
            active=True,
            hours_study=0.0,
            hours_project=0.0,
            hours_lab_prep=0.0
        )
        self.course3 = Course.objects.create(
            program=self.program1,
            code_gr="CS201",
            code_en="CS201",
            semester=2,
            title_gr="Δομές Δεδομένων",
            title_en="Data Structures",
            ects_credits=5,
            active=True,
            hours_study=0.0,
            hours_project=0.0,
            hours_lab_prep=0.0
        )
        
        self.student = Student.objects.create(
            email="it1234@hua.gr",
            given_name="John",
            surname="Doe",
            program=self.program1,
            reg_num="1234",
            semester=1
        )
        # Save password on the user created by student's save() method
        self.user = self.student.user
        self.user.set_password("Password123!!")
        self.user.save()

    def test_student_form_fields(self):
        # Instantiate form for student
        form = StudentCourseRecognitionRequestForm(student=self.student)
        
        # Student identity and study program come from the student profile.
        self.assertNotIn("full_name", form.fields)
        self.assertNotIn("program", form.fields)
        self.assertIn("course", form.fields)

        # The autocomplete queryset contains only courses from the student's program and semester.
        course_ids = set(form.fields["course"].queryset.values_list("id", flat=True))
        self.assertIn(self.course1.id, course_ids)
        self.assertNotIn(self.course2.id, course_ids)
        self.assertNotIn(self.course3.id, course_ids)

        # Choices are loaded dynamically by django-autocomplete-light.
        rendered_course_field = str(form["course"])
        self.assertIn(reverse("course_recognition:student_course_autocomplete"), rendered_course_field)
        self.assertNotIn(f'value="{self.course1.id}"', rendered_course_field)

    def test_student_form_disables_empty_course_dropdown(self):
        self.student.semester = 12
        self.student.save(update_fields=["semester"])

        form = StudentCourseRecognitionRequestForm(student=self.student)

        self.assertEqual(form.fields["course"].queryset.count(), 0)
        self.assertIn("disabled", form.fields["course"].widget.attrs)
        self.assertEqual(
            str(form.fields["course"].help_text),
            "Δεν βρέθηκαν μαθήματα για το πρόγραμμα σπουδών και το εξάμηνο του φοιτητή.",
        )

    def test_course_assignment_import_skips_existing_assignments(self):
        professor = StaffMember.objects.create(
            email="assignment-professor@hua.gr",
            given_name="Assignment",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        self.course1.assigned_to.add(professor)

        upload = SimpleUploadedFile(
            "assignments.csv",
            (
                "course_code,professor_email\n"
                "CS101,assignment-professor@hua.gr\n"
                "CS201,assignment-professor@hua.gr\n"
            ).encode("utf-8"),
            content_type="text/csv",
        )
        dataset = CourseInstructorAssignmentResource.dataset_from_upload(upload)
        resource = CourseInstructorAssignmentResource(program_ids=[self.program1.id])

        imported_count, unchanged_count, errors, unchanged_messages = resource.import_assignments(dataset)

        self.assertEqual(imported_count, 1)
        self.assertEqual(unchanged_count, 1)
        self.assertEqual(errors, [])
        self.assertEqual(len(unchanged_messages), 1)
        self.assertIn("είναι ήδη υπεύθυνος", unchanged_messages[0])
        self.assertTrue(self.course3.assigned_to.filter(pk=professor.pk).exists())

    def test_english_translations(self):
        from django.utils.translation import activate, deactivate
        activate('en')
        try:
            form = StudentCourseRecognitionRequestForm(student=self.student)
            
            # Test that labels translate to English
            self.assertEqual(str(form["course_description_file"].label), "Course description file")
            self.assertEqual(str(form["transcript_file"].label), "Transcript file")
            self.assertEqual(str(form["degree_file"].label), "Degree file")

            # Test StudyProgram translations
            self.assertEqual(str(self.student.program), "Undergraduate CS")

            # Test Admin forms translations
            from myprofile.forms_admin import AdminSecretariatUserForm, AdminStudentUserForm
            sec_form = AdminSecretariatUserForm()
            stud_form = AdminStudentUserForm()
            self.assertEqual(str(sec_form["password_confirm"].label), "Confirm password")
            self.assertEqual(str(stud_form["password_confirm"].label), "Confirm password")

            invalid_student_form = AdminStudentUserForm(data={})
            invalid_secretariat_form = AdminSecretariatUserForm(data={})
            self.assertFalse(invalid_student_form.is_valid())
            self.assertFalse(invalid_secretariat_form.is_valid())
            self.assertIn("Please fill out this field.", str(invalid_student_form.errors["given_name"]))
            self.assertIn("Please fill out this field.", str(invalid_student_form.errors["semester"]))
            self.assertIn("Please fill out this field.", str(invalid_secretariat_form.errors["departments"]))

            # Test choice field labels
            from myprofile.forms_admin import StudyProgramChoiceField
            choice_field = StudyProgramChoiceField(queryset=None)
            self.assertEqual(choice_field.label_from_instance(self.program1), "Undergraduate Study Program")
            self.assertEqual(choice_field.label_from_instance(self.program2), "Postgraduate Study Program")
        finally:
            deactivate()

    def test_admin_user_forms_validate_password_complexity(self):
        from myprofile.forms_admin import AdminSecretariatUserForm, AdminStudentUserForm

        weak_password = "weakpass"
        secretariat_form = AdminSecretariatUserForm(
            data={
                "given_name": "Secretariat",
                "surname": "User",
                "username": "secretariat-user",
                "email": "secretariat-user@hua.gr",
                "password": weak_password,
                "password_confirm": weak_password,
                "program": self.program1.id,
                "departments": [self.dept.id],
            }
        )
        student_form = AdminStudentUserForm(
            data={
                "given_name": "Student",
                "surname": "User",
                "email": "student-user@hua.gr",
                "password": weak_password,
                "password_confirm": weak_password,
                "reg_num": "2022999",
                "program": self.program1.id,
                "semester": 1,
            }
        )

        self.assertFalse(secretariat_form.is_valid())
        self.assertFalse(student_form.is_valid())
        self.assertIn("Δεν έχετε χρησιμοποιήσει τουλάχιστον ένα ψηφίο", str(secretariat_form.errors["password"]))
        self.assertIn("Δεν έχετε χρησιμοποιήσει τουλάχιστον ένα ψηφίο", str(student_form.errors["password"]))

        invalid_reg_num_form = AdminStudentUserForm(
            data={
                "given_name": "Student",
                "surname": "User",
                "email": "student-user-2@hua.gr",
                "password": "Password123!!",
                "password_confirm": "Password123!!",
                "reg_num": "it2022999",
                "program": self.program1.id,
                "semester": 1,
            }
        )

        self.assertFalse(invalid_reg_num_form.is_valid())
        self.assertIn("Ο αριθμός μητρώου πρέπει να περιέχει μόνο αριθμούς", str(invalid_reg_num_form.errors["reg_num"]))

    def test_student_form_clean_valid(self):
        form_data = {
            "course": self.course1.id,
            "title_original_course": "Introduction to Computers",
            "institution": "UOA",
            "school": "Sciences",
            "department": "Informatics",
            "instructors": "Dr. Smith",
            "academic_year": "1",
            "academic_semester": "WINTER",
            "grade_theory": 8.5,
            "average_grade": 8.5,
            "hours_theory": 3.0,
            "description": "Basic computer concepts course",
        }
        form_files = {
            "course_description_file": SimpleUploadedFile("desc.pdf", b"file_content"),
            "transcript_file": SimpleUploadedFile("transcript.pdf", b"file_content"),
            "degree_file": SimpleUploadedFile("degree.pdf", b"file_content"),
        }
        form = StudentCourseRecognitionRequestForm(form_data, form_files, student=self.student)
        self.assertTrue(form.is_valid(), form.errors)

    def test_student_form_clean_invalid_course_program_mismatch(self):
        form_data = {
            # course2 belongs to program2, but program1 is selected
            "course": self.course2.id,
            "title_original_course": "Introduction to Computers",
            "institution": "UOA",
            "school": "Sciences",
            "department": "Informatics",
            "instructors": "Dr. Smith",
            "academic_year": "1",
            "academic_semester": "WINTER",
            "grade_theory": 8.5,
            "average_grade": 8.5,
            "hours_theory": 3.0,
            "description": "Basic computer concepts course",
        }
        form_files = {
            "course_description_file": SimpleUploadedFile("desc.pdf", b"file_content"),
            "transcript_file": SimpleUploadedFile("transcript.pdf", b"file_content"),
            "degree_file": SimpleUploadedFile("degree.pdf", b"file_content"),
        }
        form = StudentCourseRecognitionRequestForm(form_data, form_files, student=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn("course", form.errors)
        self.assertEqual(
            form.errors["course"][0],
            "Το μάθημα δεν ανήκει στο πρόγραμμα σπουδών και το εξάμηνο του φοιτητή."
        )

    def test_student_form_clean_invalid_course_semester_mismatch(self):
        form_data = {
            "course": self.course3.id,
            "title_original_course": "Data Structures",
            "institution": "UOA",
            "school": "Sciences",
            "department": "Informatics",
            "instructors": "Dr. Smith",
            "academic_year": "1",
            "academic_semester": "WINTER",
            "grade_theory": 8.5,
            "average_grade": 8.5,
            "hours_theory": 3.0,
            "description": "Data structures course",
        }
        form_files = {
            "course_description_file": SimpleUploadedFile("desc.pdf", b"file_content"),
            "transcript_file": SimpleUploadedFile("transcript.pdf", b"file_content"),
            "degree_file": SimpleUploadedFile("degree.pdf", b"file_content"),
        }
        form = StudentCourseRecognitionRequestForm(form_data, form_files, student=self.student)
        self.assertFalse(form.is_valid())
        self.assertIn("course", form.errors)
        self.assertEqual(
            form.errors["course"][0],
            "Το μάθημα δεν ανήκει στο πρόγραμμα σπουδών και το εξάμηνο του φοιτητή."
        )

    def test_student_form_rejects_grades_and_hours_outside_allowed_ranges(self):
        form_data = {
            "course": self.course1.id,
            "title_original_course": "Introduction to Computers",
            "institution": "UOA",
            "school": "Sciences",
            "department": "Informatics",
            "instructors": "Dr. Smith",
            "academic_year": "1",
            "academic_semester": "WINTER",
            "grade_theory": 11,
            "grade_lab": -1,
            "average_grade": 10.5,
            "hours_theory": 0,
            "hours_lab": 4,
            "description": "Basic computer concepts course",
        }
        form_files = {
            "course_description_file": SimpleUploadedFile("desc.pdf", b"file_content"),
            "transcript_file": SimpleUploadedFile("transcript.pdf", b"file_content"),
            "degree_file": SimpleUploadedFile("degree.pdf", b"file_content"),
        }
        form = StudentCourseRecognitionRequestForm(form_data, form_files, student=self.student)

        self.assertFalse(form.is_valid())
        for field in ("grade_theory", "grade_lab", "average_grade"):
            self.assertIn(field, form.errors)
            self.assertIn("Η τιμή πρέπει να είναι από 0 έως 10.", form.errors[field])
        for field in ("hours_theory", "hours_lab"):
            self.assertIn(field, form.errors)
            self.assertIn("Η τιμή πρέπει να είναι από 1 έως 3.", form.errors[field])

    def test_recommendation_form_theory_choices(self):
        form = RecommendationForm()
        theoretical_part_choices = dict(form.fields["theoretical_part"].choices)
        
        # Verify NOT_APPLICABLE is not in choices
        self.assertNotIn("NOT_APPLICABLE", theoretical_part_choices)
        self.assertIn("COMPATIBLE", theoretical_part_choices)
        self.assertIn("NOT_COMPATIBLE", theoretical_part_choices)

    def test_recommendation_requires_grade_when_approved(self):
        form = RecommendationForm(
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "comments": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("grade", form.errors)
        self.assertEqual(
            form.errors["grade"][0],
            "Ο βαθμός αναγνώρισης είναι υποχρεωτικός όταν η εισήγηση εγκρίνεται.",
        )

        form_with_grade = RecommendationForm(
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 8,
                "comments": "",
            }
        )
        self.assertTrue(form_with_grade.is_valid(), form_with_grade.errors)

        rejected_form_with_grade = RecommendationForm(
            {
                "theoretical_part": CourseRecognitionRecommendation.NOT_COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "grade": 8,
                "comments": "",
            }
        )
        self.assertFalse(rejected_form_with_grade.is_valid())
        self.assertIn("grade", rejected_form_with_grade.errors)
        self.assertEqual(
            rejected_form_with_grade.errors["grade"][0],
            "Ο βαθμός αναγνώρισης συμπληρώνεται μόνο όταν η εισήγηση εγκρίνεται.",
        )

    def test_recommendation_grade_must_be_between_five_and_ten(self):
        form = RecommendationForm(
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 4,
                "comments": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("grade", form.errors)
        self.assertIn("Η τιμή πρέπει να είναι από 5 έως 10.", form.errors["grade"])

        form = RecommendationForm(
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 11,
                "comments": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("grade", form.errors)
        self.assertIn("Η τιμή πρέπει να είναι από 5 έως 10.", form.errors["grade"])

    def test_custom_auth_backend(self):
        backend = CustomAuthBackend()
        
        # Test authenticating with username
        user = backend.authenticate(None, username=self.user.username, password="Password123!!")
        self.assertEqual(user, self.user)
        
        # Test authenticating with email
        user_by_email = backend.authenticate(None, username="it1234@hua.gr", password="Password123!!")
        self.assertEqual(user_by_email, self.user)

    def test_logout_renders_confirmation_after_session_is_cleared(self):
        from django.utils.translation import deactivate
        self.client.force_login(self.user)

        try:
            response = self.client.get("/en/logout")

            self.assertEqual(response.status_code, 302)
            self.assertNotIn("_auth_user_id", self.client.session)
            self.assertIn("/en/accounts/login/?next=/en/", response["Location"])
        finally:
            deactivate()

    def test_student_profile_blocks_accidental_secretariat_access(self):
        secretariat = Secretariat.objects.create(user=self.user)
        secretariat.programs.add(self.program1)

        self.assertEqual(course_recognition_role(self.user), "student")

        self.client.force_login(self.user)
        self.assertRedirects(
            self.client.get(reverse("myprofile:index")),
            reverse("myprofile:student_dashboard"),
        )
        self.assertEqual(
            self.client.get(reverse("myprofile:student_dashboard")).status_code,
            200,
        )
        self.assertNotEqual(
            self.client.get(reverse("myprofile:secretariat_dashboard")).status_code,
            200,
        )
        self.assertNotEqual(
            self.client.get(reverse("course_recognition:secretariat_requests")).status_code,
            200,
        )

    def create_request(self, student, course, title):
        filename_prefix = title.lower().replace(" ", "_")
        return CourseRecognitionRequest.objects.create(
            student=student,
            full_name=student.display_name,
            course=course,
            title_original_course=title,
            institution="Test Institution",
            school="Test School",
            department="Test Department",
            instructors="Test Instructor",
            academic_year=CourseRecognitionRequest.YEAR_1,
            academic_semester=CourseRecognitionRequest.WINTER,
            grade_theory=8,
            average_grade=8,
            hours_theory=3,
            description="Test description",
            course_description_file=f"course_recognition/course_descriptions/{filename_prefix}_desc.pdf",
            transcript_file=f"course_recognition/transcripts/{filename_prefix}_transcript.pdf",
            degree_file=f"course_recognition/degrees/{filename_prefix}_degree.pdf",
        )

    def test_request_displays_current_student_name(self):
        request_obj = self.create_request(self.student, self.course1, "Current student name")
        request_obj.full_name = "Old Student Name"
        request_obj.save(update_fields=["full_name", "updated_at"])

        self.student.given_name = "Demo"
        self.student.surname = "Student"
        self.student.save()

        request_obj.refresh_from_db()

        self.assertEqual(request_obj.student_display_name, "Demo Student")

    def test_student_sees_only_own_requests(self):
        other_student = Student.objects.create(
            email="it5678@hua.gr",
            given_name="Jane",
            surname="Doe",
            program=self.program1,
            reg_num="5678",
        )
        own_request = self.create_request(self.student, self.course1, "Own request")
        other_request = self.create_request(other_student, self.course2, "Other request")

        self.client.force_login(self.user)
        dashboard = self.client.get(reverse("myprofile:student_dashboard"))
        self.assertContains(dashboard, own_request.course, count=1)
        self.assertContains(
            dashboard,
            reverse("course_recognition:student_request_detail", args=(own_request.id,)),
        )
        self.assertNotContains(dashboard, other_request.course)
        self.assertNotContains(dashboard, "View all")
        self.assertEqual(self.client.get("/el/student/course-recognition/").status_code, 404)
        detail = self.client.get(reverse("course_recognition:student_request_detail", args=(own_request.id,)))
        self.assertContains(detail, self.student.reg_num)
        self.assertContains(
            detail,
            reverse("course_recognition:student_request_update", args=(own_request.id,)),
        )
        self.assertRedirects(
            self.client.get(reverse("myprofile:index")),
            reverse("myprofile:student_dashboard"),
        )
        self.assertEqual(
            self.client.get(
                reverse("course_recognition:student_request_update", args=(other_request.id,))
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(
                reverse("course_recognition:student_request_detail", args=(other_request.id,))
            ).status_code,
            404,
        )

    def test_professor_sees_only_requests_for_assigned_courses(self):
        professor = StaffMember.objects.create(
            email="professor@hua.gr",
            given_name="Test",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        self.course1.assigned_to.add(professor)
        assigned_request = self.create_request(self.student, self.course1, "Assigned course")
        other_request = self.create_request(self.student, self.course2, "Other course")

        queryset = _professor_queryset(professor.user)

        self.assertIn(assigned_request, queryset)
        self.assertNotIn(other_request, queryset)
        self.client.force_login(professor.user)
        dashboard = self.client.get(reverse("myprofile:professor_dashboard"))
        self.assertContains(dashboard, assigned_request.course)
        self.assertNotContains(dashboard, other_request.course)
        self.assertNotContains(dashboard, "Αιτήσεις αναγνώρισης")
        self.assertNotContains(dashboard, "Προβολή όλων")
        self.assertRedirects(
            self.client.get(reverse("myprofile:index")),
            reverse("myprofile:professor_dashboard"),
        )
        self.assertTrue(
            reverse("course_recognition:professor_recommendation", args=(assigned_request.id,))
            .endswith(f"/professor/course-recognition/{assigned_request.id}/recommendation/")
        )

        recommendation = self.client.get(
            reverse("course_recognition:professor_recommendation", args=(assigned_request.id,))
        )
        self.assertContains(recommendation, reverse("myprofile:professor_dashboard"))
        self.assertContains(recommendation, "Ονοματεπώνυμο")
        self.assertContains(recommendation, assigned_request.student_display_name)
        self.assertContains(recommendation, self.student.reg_num)
        self.assertContains(recommendation, self.student.program)
        self.assertNotContains(recommendation, ">Φοιτητής<")
        self.assertContains(recommendation, assigned_request.institution)
        self.assertContains(recommendation, assigned_request.description)
        self.assertContains(recommendation, "assigned_course_desc.pdf")
        self.assertTrue(
            can_download(
                ["course_recognition", "course_descriptions", "assigned_course_desc.pdf"],
                professor.user,
            )
        )
        self.assertFalse(
            can_download(
                ["course_recognition", "transcripts", "assigned_course_transcript.pdf"],
                User.objects.create_user(username="unrelated"),
            )
        )

    def test_final_recommendation_locks_student_edit_and_is_visible(self):
        request_obj = self.create_request(self.student, self.course1, "Final request")
        request_obj.status = CourseRecognitionRequest.APPROVED
        request_obj.save(update_fields=["status", "updated_at"])
        CourseRecognitionRecommendation.objects.create(
            request=request_obj,
            theoretical_part=CourseRecognitionRecommendation.COMPATIBLE,
            laboratory_part=CourseRecognitionRecommendation.NOT_APPLICABLE,
            approval=True,
            grade=9,
            comments="Approved recommendation comments",
        )

        self.client.force_login(self.user)
        detail = self.client.get(reverse("course_recognition:student_request_detail", args=(request_obj.id,)))

        self.assertContains(detail, "Approved recommendation comments")
        self.assertContains(detail, "9")
        self.assertNotContains(
            detail,
            reverse("course_recognition:student_request_update", args=(request_obj.id,)),
        )
        self.assertRedirects(
            self.client.get(reverse("course_recognition:student_request_update", args=(request_obj.id,))),
            reverse("course_recognition:student_request_detail", args=(request_obj.id,)),
        )

    def test_pending_professor_recommendation_locks_student_edit(self):
        professor = StaffMember.objects.create(
            user=User.objects.create_user(
                username="student-lock-professor",
                email="student-lock-professor@hua.gr",
                password="Password123!!",
            ),
            email="student-lock-professor@hua.gr",
            given_name="Student",
            surname="Lock Professor",
            title="Professor",
            internal_department=self.dept,
        )
        request_obj = self.create_request(self.student, self.course1, "Student pending lock")
        CourseRecognitionRecommendation.objects.create(
            request=request_obj,
            professor=professor,
            theoretical_part=CourseRecognitionRecommendation.COMPATIBLE,
            laboratory_part=CourseRecognitionRecommendation.NOT_APPLICABLE,
            approval=True,
            grade=8,
            comments="Pending professor recommendation",
            submitted_by_secretariat=False,
            submitted_by_user=professor.user,
        )

        self.client.force_login(self.user)
        detail = self.client.get(reverse("course_recognition:student_request_detail", args=(request_obj.id,)))
        self.assertContains(
            detail,
            "Η αίτηση δεν μπορεί να επεξεργαστεί επειδή υπάρχει εκκρεμής εισήγηση καθηγητή.",
        )
        self.assertNotContains(detail, "Pending professor recommendation")
        self.assertNotContains(
            detail,
            reverse("course_recognition:student_request_update", args=(request_obj.id,)),
        )
        self.assertRedirects(
            self.client.get(reverse("course_recognition:student_request_update", args=(request_obj.id,))),
            reverse("course_recognition:student_request_detail", args=(request_obj.id,)),
        )

    def test_final_recommendation_is_read_only_for_professor_and_secretariat(self):
        professor = StaffMember.objects.create(
            email="final-professor@hua.gr",
            given_name="Final",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        self.course1.assigned_to.add(professor)
        request_obj = self.create_request(self.student, self.course1, "Read only recommendation")
        request_obj.status = CourseRecognitionRequest.REJECTED
        request_obj.save(update_fields=["status", "updated_at"])
        recommendation = CourseRecognitionRecommendation.objects.create(
            request=request_obj,
            professor=professor,
            theoretical_part=CourseRecognitionRecommendation.NOT_COMPATIBLE,
            laboratory_part=CourseRecognitionRecommendation.NOT_APPLICABLE,
            approval=False,
            comments="Rejected recommendation comments",
        )

        self.client.force_login(professor.user)
        professor_response = self.client.post(
            reverse("course_recognition:professor_recommendation", args=(request_obj.id,)),
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 10,
                "comments": "Should not replace comments",
            },
        )
        recommendation.refresh_from_db()
        self.assertEqual(professor_response.status_code, 200)
        self.assertContains(professor_response, "Rejected recommendation comments")
        self.assertNotContains(professor_response, 'name="grade"')
        self.assertEqual(recommendation.comments, "Rejected recommendation comments")

        secretary = User.objects.create_user(username="secretary-final", email="secretary-final@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        self.client.force_login(secretary)
        secretariat_response = self.client.post(
            reverse("course_recognition:secretariat_recommendation", args=(request_obj.id,)),
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 10,
                "comments": "Secretariat should not replace comments",
            },
        )
        recommendation.refresh_from_db()
        self.assertEqual(secretariat_response.status_code, 200)
        self.assertContains(secretariat_response, "Rejected recommendation comments")
        self.assertNotContains(secretariat_response, 'name="grade"')
        self.assertEqual(recommendation.comments, "Rejected recommendation comments")

    def test_recommendation_requires_protocol_number(self):
        professor = StaffMember.objects.create(
            email="protocol-professor@hua.gr",
            given_name="Protocol",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        self.course1.assigned_to.add(professor)
        professor_request = self.create_request(self.student, self.course1, "Professor missing protocol")

        self.client.force_login(professor.user)
        professor_response = self.client.post(
            reverse("course_recognition:professor_recommendation", args=(professor_request.id,)),
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 9,
                "comments": "Should be blocked",
            },
        )
        professor_request.refresh_from_db()
        self.assertEqual(professor_response.status_code, 200)
        self.assertContains(
            professor_response,
            "Δεν μπορεί να γίνει εισήγηση πριν καταχωρηθεί αριθμός πρωτοκόλλου.",
        )
        self.assertEqual(professor_request.status, CourseRecognitionRequest.UNDER_REVIEW)
        self.assertFalse(CourseRecognitionRecommendation.objects.filter(request=professor_request).exists())

        secretary = User.objects.create_user(username="secretary-missing-protocol", email="secretary-missing-protocol@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        secretariat_request = self.create_request(self.student, self.course1, "Secretariat missing protocol")

        self.client.force_login(secretary)
        secretariat_response = self.client.post(
            reverse("course_recognition:secretariat_recommendation", args=(secretariat_request.id,)),
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 9,
                "comments": "Should also be blocked",
            },
        )
        secretariat_request.refresh_from_db()
        self.assertEqual(secretariat_response.status_code, 200)
        self.assertContains(
            secretariat_response,
            "Δεν μπορεί να γίνει εισήγηση πριν καταχωρηθεί αριθμός πρωτοκόλλου.",
        )
        self.assertEqual(secretariat_request.status, CourseRecognitionRequest.UNDER_REVIEW)
        self.assertFalse(CourseRecognitionRecommendation.objects.filter(request=secretariat_request).exists())

    def test_protocol_field_accepts_only_digits_in_browser(self):
        form = SecretariatProtocolForm()
        attrs = form.fields["protocol_number"].widget.attrs

        self.assertEqual(attrs["inputmode"], "numeric")
        self.assertEqual(attrs["pattern"], "[1-9][0-9]*")
        self.assertEqual(attrs["oninput"], "this.value = this.value.replace(/\\D/g, '');")

    def test_professor_recommendation_stays_pending_until_secretariat_decision(self):
        professor = StaffMember.objects.create(
            email="pending-professor@hua.gr",
            given_name="Pending",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        self.course1.assigned_to.add(professor)
        request_obj = self.create_request(self.student, self.course1, "Pending professor decision")
        request_obj.protocol_number = "321"
        request_obj.save(update_fields=["protocol_number", "updated_at"])

        self.client.force_login(professor.user)
        professor_response = self.client.post(
            reverse("course_recognition:professor_recommendation", args=(request_obj.id,)),
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 8,
                "comments": "Professor pending recommendation",
            },
        )
        self.assertRedirects(
            professor_response,
            reverse("course_recognition:professor_recommendation", args=(request_obj.id,)),
        )
        request_obj.refresh_from_db()
        recommendation = CourseRecognitionRecommendation.objects.get(request=request_obj)
        self.assertEqual(request_obj.status, CourseRecognitionRequest.UNDER_REVIEW)
        self.assertFalse(recommendation.submitted_by_secretariat)

        secretary = User.objects.create_user(username="secretary-pending", email="secretary-pending@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        self.client.force_login(secretary)
        pending_detail = self.client.get(reverse("course_recognition:secretariat_recommendation", args=(request_obj.id,)))
        self.assertContains(pending_detail, "Professor pending recommendation")
        self.assertContains(pending_detail, reverse("course_recognition:secretariat_accept_recommendation", args=(request_obj.id,)))
        self.assertContains(pending_detail, reverse("course_recognition:secretariat_reject_recommendation", args=(request_obj.id,)))
        self.assertNotContains(pending_detail, 'name="grade"')

        reject_response = self.client.post(reverse("course_recognition:secretariat_reject_recommendation", args=(request_obj.id,)))
        self.assertRedirects(reject_response, reverse("course_recognition:secretariat_requests"), fetch_redirect_response=False)
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, CourseRecognitionRequest.UNDER_REVIEW)
        self.assertFalse(CourseRecognitionRecommendation.objects.filter(request=request_obj).exists())

        CourseRecognitionRecommendation.objects.create(
            request=request_obj,
            professor=professor,
            theoretical_part=CourseRecognitionRecommendation.COMPATIBLE,
            laboratory_part=CourseRecognitionRecommendation.NOT_APPLICABLE,
            approval=True,
            grade=8,
            comments="Accepted professor recommendation",
        )
        accept_response = self.client.post(reverse("course_recognition:secretariat_accept_recommendation", args=(request_obj.id,)))
        self.assertRedirects(accept_response, reverse("course_recognition:secretariat_requests"), fetch_redirect_response=False)
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, CourseRecognitionRequest.APPROVED)

    def test_withdrawn_request_is_read_only_for_professor(self):
        professor = StaffMember.objects.create(
            email="withdrawn-professor@hua.gr",
            given_name="Withdrawn",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        self.course1.assigned_to.add(professor)
        request_obj = self.create_request(self.student, self.course1, "Withdrawn professor request")
        request_obj.status = CourseRecognitionRequest.WITHDRAWN
        request_obj.withdrawn_by = professor.user
        request_obj.withdrawal_reason = "Professor should only read this withdrawal reason"
        request_obj.save(update_fields=["status", "withdrawn_by", "withdrawal_reason", "updated_at"])

        self.client.force_login(professor.user)
        response = self.client.post(
            reverse("course_recognition:professor_recommendation", args=(request_obj.id,)),
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 10,
                "comments": "Should not create recommendation",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, request_obj.title_original_course)
        self.assertContains(response, "Professor should only read this withdrawal reason")
        self.assertContains(response, professor.user.username)
        self.assertNotContains(response, 'name="grade"')
        self.assertFalse(CourseRecognitionRecommendation.objects.filter(request=request_obj).exists())

    def test_student_sees_withdrawal_details(self):
        secretary = User.objects.create_user(
            username="secretary-withdrawn",
            email="secretary-withdrawn@hua.gr",
            first_name="Maria",
            last_name="Secretariat",
        )
        request_obj = self.create_request(self.student, self.course1, "Withdrawn student visible request")
        request_obj.status = CourseRecognitionRequest.WITHDRAWN
        request_obj.withdrawn_by = secretary
        request_obj.withdrawal_reason = "Student should see this withdrawal reason"
        request_obj.save(update_fields=["status", "withdrawn_by", "withdrawal_reason", "updated_at"])

        self.client.force_login(self.user)
        response = self.client.get(reverse("course_recognition:student_request_detail", args=(request_obj.id,)))

        self.assertContains(response, "Maria Secretariat")
        self.assertContains(response, "Student should see this withdrawal reason")

    def test_secretariat_recommendation_shows_submitter_full_name(self):
        secretary = User.objects.create_user(
            username="secretary-recommendation-name",
            email="secretary-recommendation-name@hua.gr",
            first_name="Eleni",
            last_name="Secretariat",
        )
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        request_obj = self.create_request(self.student, self.course1, "Secretariat named recommendation")
        request_obj.protocol_number = "200"
        request_obj.save(update_fields=["protocol_number", "updated_at"])

        self.client.force_login(secretary)
        self.client.post(
            reverse("course_recognition:secretariat_recommendation", args=(request_obj.id,)),
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 8,
                "comments": "Named secretariat recommendation",
            },
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("course_recognition:student_request_detail", args=(request_obj.id,)))
        recommendation = CourseRecognitionRecommendation.objects.get(request=request_obj)

        self.assertEqual(recommendation.submitted_by_user, secretary)
        self.assertContains(response, "Eleni Secretariat")
        self.assertContains(response, "Named secretariat recommendation")

    def test_secretariat_cannot_edit_protocol_after_final_recommendation(self):
        secretary = User.objects.create_user(username="secretary-protocol", email="secretary-protocol@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        request_obj = self.create_request(self.student, self.course1, "Final protocol request")
        request_obj.status = CourseRecognitionRequest.APPROVED
        request_obj.save(update_fields=["status", "updated_at"])
        CourseRecognitionRecommendation.objects.create(
            request=request_obj,
            theoretical_part=CourseRecognitionRecommendation.COMPATIBLE,
            laboratory_part=CourseRecognitionRecommendation.NOT_APPLICABLE,
            approval=True,
            grade=9,
            comments="Final protocol recommendation",
        )

        self.client.force_login(secretary)
        request_list = self.client.get(reverse("course_recognition:secretariat_requests"))
        self.assertNotContains(
            request_list,
            reverse("course_recognition:secretariat_protocol", args=(request_obj.id,)),
        )
        self.assertRedirects(
            self.client.get(reverse("course_recognition:secretariat_protocol", args=(request_obj.id,))),
            (
                reverse("course_recognition:secretariat_recommendation", args=(request_obj.id,))
                + "?next=%2Fel%2Fsecretariat%2Fcourse-recognition%2F"
            ),
        )

    def test_secretariat_cannot_edit_existing_protocol_number(self):
        secretary = User.objects.create_user(username="secretary-existing-protocol", email="secretary-existing-protocol@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        request_obj = self.create_request(self.student, self.course1, "Existing protocol request")
        request_obj.protocol_number = "ADMIN-123"
        request_obj.save(update_fields=["protocol_number", "updated_at"])

        self.client.force_login(secretary)
        request_list = self.client.get(reverse("course_recognition:secretariat_requests"))
        self.assertNotContains(
            request_list,
            reverse("course_recognition:secretariat_protocol", args=(request_obj.id,)),
        )
        self.assertRedirects(
            self.client.get(reverse("course_recognition:secretariat_protocol", args=(request_obj.id,))),
            (
                reverse("course_recognition:secretariat_recommendation", args=(request_obj.id,))
                + "?next=%2Fel%2Fsecretariat%2Fcourse-recognition%2F"
            ),
        )

    def test_secretariat_sees_only_requests_for_own_programs(self):
        secretary = User.objects.create_user(
            username="secretary",
            email="secretary@hua.gr",
            password="Password123!!",
        )
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        first_request = self.create_request(self.student, self.course1, "Undergraduate request")
        second_request = self.create_request(self.student, self.course2, "Postgraduate request")

        queryset = _secretariat_queryset(secretary)

        self.assertIn(first_request, queryset)
        self.assertNotIn(second_request, queryset)
        self.client.force_login(secretary)
        dashboard = self.client.get(reverse("myprofile:secretariat_dashboard"))
        self.assertContains(dashboard, "course-recognition/")
        self.assertContains(dashboard, reverse("course_recognition:secretariat_course_assignment"))
        self.assertNotContains(dashboard, first_request.title_original_course)
        self.assertNotContains(dashboard, second_request.title_original_course)
        self.assertNotContains(dashboard, "View all")

        request_list = self.client.get(reverse("course_recognition:secretariat_requests"))
        self.assertContains(request_list, first_request.course)
        self.assertContains(request_list, self.student.reg_num)
        self.assertNotContains(request_list, second_request.course)
        self.assertNotContains(request_list, reverse("course_recognition:secretariat_course_assignment"))
        self.assertRedirects(
            self.client.get(reverse("myprofile:index")),
            reverse("myprofile:secretariat_dashboard"),
        )

    def test_secretariat_request_status_filters(self):
        secretary = User.objects.create_user(
            username="secretary-filter",
            email="secretary-filter@hua.gr",
            password="Password123!!",
        )
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        under_review = self.create_request(self.student, self.course1, "Under review request")
        completed = self.create_request(self.student, self.course1, "Completed request")
        completed.status = CourseRecognitionRequest.APPROVED
        completed.save(update_fields=["status"])
        inactive = self.create_request(self.student, self.course1, "Inactive request")
        inactive.status = CourseRecognitionRequest.WITHDRAWN
        inactive.save(update_fields=["status"])

        self.client.force_login(secretary)
        list_url = reverse("course_recognition:secretariat_requests")

        default_response = self.client.get(list_url)
        self.assertContains(default_response, under_review.title_original_course)
        self.assertNotContains(default_response, completed.title_original_course)
        self.assertNotContains(default_response, inactive.title_original_course)

        completed_response = self.client.get(f"{list_url}?status=completed")
        self.assertContains(completed_response, completed.title_original_course)
        self.assertNotContains(completed_response, under_review.title_original_course)
        self.assertNotContains(completed_response, inactive.title_original_course)

        inactive_response = self.client.get(f"{list_url}?status=inactive")
        self.assertContains(inactive_response, inactive.title_original_course)
        self.assertContains(
            inactive_response,
            reverse("course_recognition:secretariat_recommendation", args=(inactive.id,)),
        )
        self.assertContains(
            inactive_response,
            f"{reverse('course_recognition:secretariat_export_xlsx')}?status=inactive",
        )
        self.assertNotContains(
            inactive_response,
            reverse("course_recognition:secretariat_protocol", args=(inactive.id,)),
        )
        self.assertNotContains(
            inactive_response,
            reverse("course_recognition:secretariat_withdraw", args=(inactive.id,)),
        )

    def test_secretariat_actions_return_to_current_filter(self):
        secretary = User.objects.create_user(
            username="secretary-return-filter",
            email="secretary-return-filter@hua.gr",
            password="Password123!!",
        )
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        protocol_request = self.create_request(self.student, self.course1, "Protocol return request")
        recommendation_request = self.create_request(self.student, self.course1, "Recommendation return request")
        recommendation_request.protocol_number = "456"
        recommendation_request.save(update_fields=["protocol_number", "updated_at"])
        withdraw_request = self.create_request(self.student, self.course1, "Withdraw return request")
        return_url = f"{reverse('course_recognition:secretariat_requests')}?status=all"

        self.client.force_login(secretary)
        protocol_response = self.client.post(
            f"{reverse('course_recognition:secretariat_protocol', args=(protocol_request.id,))}?next={return_url}",
            {"protocol_number": "123"},
        )
        self.assertRedirects(protocol_response, return_url, fetch_redirect_response=False)

        recommendation_response = self.client.post(
            f"{reverse('course_recognition:secretariat_recommendation', args=(recommendation_request.id,))}?next={return_url}",
            {
                "theoretical_part": CourseRecognitionRecommendation.COMPATIBLE,
                "laboratory_part": CourseRecognitionRecommendation.NOT_APPLICABLE,
                "approval": "on",
                "grade": 9,
                "comments": "Approved from filter",
            },
        )
        self.assertRedirects(recommendation_response, return_url, fetch_redirect_response=False)

        withdraw_response = self.client.post(
            reverse("course_recognition:secretariat_withdraw", args=(withdraw_request.id,)),
            {
                "next": return_url,
                "withdrawal_reason": "Duplicate request",
            },
        )
        self.assertRedirects(withdraw_response, return_url, fetch_redirect_response=False)
        withdraw_request.refresh_from_db()
        self.assertEqual(withdraw_request.status, CourseRecognitionRequest.WITHDRAWN)
        self.assertEqual(withdraw_request.withdrawal_reason, "Duplicate request")
        self.assertEqual(withdraw_request.withdrawn_by, secretary)

        inactive_detail = self.client.get(
            f"{reverse('course_recognition:secretariat_recommendation', args=(withdraw_request.id,))}?next={return_url}"
        )
        self.assertContains(inactive_detail, "Duplicate request")
        self.assertContains(inactive_detail, secretary.username)

    def test_secretariat_export_xlsx(self):
        secretary = User.objects.create_user(
            username="secretary-export-xlsx",
            email="secretary-export-xlsx@hua.gr",
            password="Password123!!",
        )
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        under_review_request = self.create_request(self.student, self.course1, "Under review xlsx request")
        approved_request = self.create_request(self.student, self.course1, "Approved xlsx request")
        approved_request.status = CourseRecognitionRequest.APPROVED
        approved_request.save(update_fields=["status"])
        CourseRecognitionRecommendation.objects.create(
            request=approved_request,
            theoretical_part=CourseRecognitionRecommendation.COMPATIBLE,
            laboratory_part=CourseRecognitionRecommendation.NOT_APPLICABLE,
            approval=True,
            grade=9,
        )

        self.client.force_login(secretary)
        response = self.client.get(reverse("course_recognition:secretariat_export_xlsx") + "?status=all")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        import io
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(response.content))
        ws = wb.active
        self.assertEqual(ws.title, "Αιτήσεις Αναγνώρισης")

        rows = list(ws.values)
        headers = rows[0]
        self.assertEqual(headers[0], "ID")
        self.assertEqual(headers[1], "Ονοματεπώνυμο")
        
        self.assertEqual(len(rows), 3)

        under_review_row = [r for r in rows if r[4] == "Under review xlsx request"][0]
        self.assertEqual(under_review_row[17], "Υπό εξέταση")

        approved_row = [r for r in rows if r[4] == "Approved xlsx request"][0]
        self.assertEqual(approved_row[17], "Εγκρίθηκε")
        self.assertEqual(approved_row[18], "Εγκρίθηκε")
        self.assertEqual(approved_row[19], 9)

        ordered_response = self.client.get(
            reverse("course_recognition:secretariat_export_xlsx")
            + f"?status=all&ids={approved_request.id},{under_review_request.id}"
        )
        ordered_wb = load_workbook(io.BytesIO(ordered_response.content))
        ordered_rows = list(ordered_wb.active.values)
        self.assertEqual([ordered_rows[1][0], ordered_rows[2][0]], [approved_request.id, under_review_request.id])

    def test_secretariat_can_assign_course_to_professor(self):
        professor = StaffMember.objects.create(
            email="assigned-professor@hua.gr",
            given_name="Assigned",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        secretary = User.objects.create_user(username="secretary-assignment", email="secretary-assignment@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        form = CourseInstructorAssignmentForm(
            data={
                "course": self.course1.id,
                "instructors": professor.id,
            },
            user=secretary,
        )

        self.assertTrue(form.is_valid(), form.errors)
        course, _, _ = form.save()
        self.assertIn(professor, course.assigned_to.all())

        form_for_secretariat = CourseInstructorAssignmentForm(user=secretary)
        course_ids = set(form_for_secretariat.fields["course"].queryset.values_list("id", flat=True))
        instructor_ids = set(form_for_secretariat.fields["instructors"].queryset.values_list("id", flat=True))
        self.assertIn(self.course1.id, course_ids)
        self.assertNotIn(self.course2.id, course_ids)
        self.assertIn(professor.id, instructor_ids)

        # Choices are loaded dynamically by django-autocomplete-light.
        rendered_course_field = str(form_for_secretariat["course"])
        rendered_instructors_field = str(form_for_secretariat["instructors"])
        self.assertIn(reverse("course_recognition:secretariat_course_autocomplete"), rendered_course_field)
        self.assertIn(reverse("course_recognition:professor_autocomplete"), rendered_instructors_field)
        self.assertNotIn(f'value="{self.course1.id}"', rendered_course_field)
        self.assertNotIn(f'value="{professor.id}"', rendered_instructors_field)

        invalid_form = CourseInstructorAssignmentForm(
            data={
                "course": self.course2.id,
                "instructors": professor.id,
            },
            user=secretary,
        )
        self.assertFalse(invalid_form.is_valid())
        self.assertIn("course", invalid_form.errors)

    def test_course_assignment_adds_professor_without_removing_existing_ones(self):
        existing_professor = StaffMember.objects.create(
            email="existing-professor@hua.gr",
            given_name="Existing",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        new_professor = StaffMember.objects.create(
            email="new-professor@hua.gr",
            given_name="New",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        secretary = User.objects.create_user(username="secretary-multi-assignment", email="secretary-multi-assignment@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        self.course1.assigned_to.add(existing_professor)

        form = CourseInstructorAssignmentForm(
            data={
                "course": self.course1.id,
                "instructors": new_professor.id,
            },
            user=secretary,
        )

        self.assertTrue(form.is_valid(), form.errors)
        course, _, _ = form.save()
        self.assertIn(existing_professor, course.assigned_to.all())
        self.assertIn(new_professor, course.assigned_to.all())

    def test_secretariat_imports_course_assignments_by_course_code(self):
        professor = StaffMember.objects.create(
            email="csv-professor@hua.gr",
            given_name="Csv",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        secretary = User.objects.create_user(username="secretary-csv", email="secretary-csv@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        self.client.force_login(secretary)

        response = self.client.get(reverse("course_recognition:secretariat_course_assignment"))
        self.assertContains(response, "Import CSV")
        self.assertContains(response, 'name="import_file"')

        upload = SimpleUploadedFile(
            "assignments.csv",
            f"course_code;professor_email\n{self.course1.code_gr};{professor.email}\n".encode("utf-8"),
            content_type="text/csv",
        )
        response = self.client.post(
            reverse("course_recognition:secretariat_course_assignment"),
            {"import_assignments": "1", "import_file": upload},
        )

        self.assertRedirects(response, reverse("course_recognition:secretariat_course_assignment"))
        self.assertIn(professor, self.course1.assigned_to.all())

        mixed_professor = StaffMember.objects.create(
            email="mixed-csv-professor@hua.gr",
            given_name="Mixed",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        mixed_upload = SimpleUploadedFile(
            "mixed-assignments.csv",
            (
                "course_code;professor_email\n"
                f"{self.course3.code_gr};{mixed_professor.email}\n"
                f"WRONG999;{mixed_professor.email}\n"
                f"{self.course3.code_gr};{mixed_professor.email}\n"
            ).encode("utf-8"),
            content_type="text/csv",
        )
        response = self.client.post(
            reverse("course_recognition:secretariat_course_assignment"),
            {"import_assignments": "1", "import_file": mixed_upload},
            follow=True,
        )

        self.assertIn(mixed_professor, self.course3.assigned_to.all())
        messages_text = " ".join(str(message) for message in response.context["messages"])
        self.assertIn("Δεν βρέθηκε μάθημα με κωδικό WRONG999.", messages_text)
        self.assertIn("Προστέθηκε 1 ανάθεση.", messages_text)
        self.assertIn("είναι ήδη υπεύθυνος", messages_text)

        blocked_professor = StaffMember.objects.create(
            email="blocked-csv-professor@hua.gr",
            given_name="Blocked",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        blocked_upload = SimpleUploadedFile(
            "blocked-assignments.csv",
            f"course_code;professor_email\n{self.course2.code_gr};{blocked_professor.email}\n".encode("utf-8"),
            content_type="text/csv",
        )
        self.client.post(
            reverse("course_recognition:secretariat_course_assignment"),
            {"import_assignments": "1", "import_file": blocked_upload},
        )

        self.assertNotIn(blocked_professor, self.course2.assigned_to.all())

    def test_course_assignment_import_without_file_does_not_validate_dropdown_form(self):
        secretary = User.objects.create_user(username="secretary-import-empty", email="secretary-import-empty@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.programs.add(self.program1)
        self.client.force_login(secretary)

        response = self.client.post(
            reverse("course_recognition:secretariat_course_assignment"),
            {"import_assignments": "1"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Πρέπει να επιλεχθεί κάποιο αρχείο.")
        self.assertNotContains(response, "Αυτό το πεδίο είναι απαραίτητο.")

    def test_admin_uses_custom_dashboard_and_request_edit(self):
        admin = User.objects.create_superuser(
            username="admin",
            email="admin@hua.gr",
            password="Password123!!",
        )
        secretary = User.objects.create_user(username="secretary", email="secretary@hua.gr")
        secretariat = Secretariat.objects.create(user=secretary)
        secretariat.departments.add(self.dept)
        request_obj = self.create_request(self.student, self.course1, "Admin editable request")

        self.client.force_login(admin)
        self.assertRedirects(
            self.client.get(reverse("myprofile:index")),
            reverse("myprofile:admin_dashboard"),
        )
        dashboard = self.client.get(reverse("myprofile:admin_dashboard"))
        self.assertContains(dashboard, reverse("myprofile:admin_secretariat_users"))
        self.assertContains(dashboard, reverse("myprofile:admin_student_users"))
        self.assertContains(dashboard, reverse("course_recognition:admin_requests"))
        secretariat_users = self.client.get(reverse("myprofile:admin_secretariat_users"))
        self.assertContains(secretariat_users, reverse("myprofile:admin_secretariat_create"))
        self.assertContains(secretariat_users, reverse("myprofile:admin_secretariat_update", args=(secretariat.id,)))
        student_users = self.client.get(reverse("myprofile:admin_student_users"))
        self.assertContains(student_users, reverse("myprofile:admin_student_create"))
        self.assertContains(student_users, reverse("myprofile:admin_student_update", args=(self.student.id,)))
        self.assertContains(student_users, self.student.reg_num)
        request_list = self.client.get(reverse("course_recognition:admin_requests"))
        self.assertContains(request_list, self.student.reg_num)
        admin_edit = self.client.get(reverse("course_recognition:admin_request_update", args=(request_obj.id,)))
        self.assertNotContains(admin_edit, 'name="status"')
        self.assertEqual(self.client.get("/el/admin/").status_code, 404)
        self.assertTrue(
            reverse("course_recognition:admin_request_update", args=(request_obj.id,))
            .endswith(f"/admin/course-recognition/{request_obj.id}/edit/")
        )

    def test_admin_can_only_view_finalized_request(self):
        admin = User.objects.create_superuser(
            username="final-admin",
            email="final-admin@hua.gr",
            password="Password123!!",
        )
        request_obj = self.create_request(self.student, self.course1, "Final admin request")
        request_obj.status = CourseRecognitionRequest.APPROVED
        request_obj.save(update_fields=["status", "updated_at"])
        CourseRecognitionRecommendation.objects.create(
            request=request_obj,
            theoretical_part=CourseRecognitionRecommendation.COMPATIBLE,
            laboratory_part=CourseRecognitionRecommendation.NOT_APPLICABLE,
            approval=True,
            grade=9,
            comments="Admin should only view this recommendation",
        )

        self.client.force_login(admin)
        completed_filter_url = f"{reverse('course_recognition:admin_requests')}?status=completed"
        request_list = self.client.get(completed_filter_url)
        self.assertContains(
            request_list,
            (
                reverse("course_recognition:admin_request_detail", args=(request_obj.id,))
                + "?next=/el/admin/course-recognition/%3Fstatus%3Dcompleted"
            ),
        )
        self.assertNotContains(
            request_list,
            reverse("course_recognition:admin_request_update", args=(request_obj.id,)),
        )

        detail = self.client.get(
            (
                reverse("course_recognition:admin_request_detail", args=(request_obj.id,))
                + f"?next={completed_filter_url}"
            )
        )
        self.assertContains(detail, completed_filter_url)
        self.assertContains(detail, "Admin should only view this recommendation")
        self.assertNotContains(
            detail,
            reverse("course_recognition:admin_request_update", args=(request_obj.id,)),
        )
        self.assertRedirects(
            self.client.get(reverse("course_recognition:admin_request_update", args=(request_obj.id,))),
            (
                reverse("course_recognition:admin_request_detail", args=(request_obj.id,))
                + "?next=%2Fel%2Fadmin%2Fcourse-recognition%2F"
            ),
        )

    def test_admin_cannot_edit_request_with_pending_professor_recommendation(self):
        admin = User.objects.create_superuser(
            username="pending-admin",
            email="pending-admin@hua.gr",
            password="Password123!!",
        )
        professor = StaffMember.objects.create(
            user=User.objects.create_user(
                username="pending-professor",
                email="pending-professor@hua.gr",
                password="Password123!!",
            ),
            email="pending-professor@hua.gr",
            given_name="Pending",
            surname="Professor",
            title="Professor",
            internal_department=self.dept,
        )
        request_obj = self.create_request(self.student, self.course1, "Pending professor recommendation request")
        CourseRecognitionRecommendation.objects.create(
            request=request_obj,
            professor=professor,
            theoretical_part=CourseRecognitionRecommendation.COMPATIBLE,
            laboratory_part=CourseRecognitionRecommendation.NOT_APPLICABLE,
            approval=True,
            grade=8,
            comments="Pending professor recommendation",
            submitted_by_secretariat=False,
            submitted_by_user=professor.user,
        )

        self.client.force_login(admin)
        edit_url = reverse("course_recognition:admin_request_update", args=(request_obj.id,))
        detail_url = reverse("course_recognition:admin_request_detail", args=(request_obj.id,))
        list_response = self.client.get(reverse("course_recognition:admin_requests"))
        self.assertNotContains(list_response, edit_url)
        self.assertRedirects(
            self.client.get(edit_url),
            detail_url + "?next=%2Fel%2Fadmin%2Fcourse-recognition%2F",
        )

        self.client.post(reverse("course_recognition:admin_reject_recommendation", args=(request_obj.id,)))
        request_obj.refresh_from_db()
        self.assertEqual(request_obj.status, CourseRecognitionRequest.UNDER_REVIEW)
        self.assertFalse(CourseRecognitionRecommendation.objects.filter(request=request_obj).exists())

        edit_response = self.client.get(edit_url)
        self.assertEqual(edit_response.status_code, 200)
        self.assertContains(edit_response, "Pending professor recommendation request")

    def test_admin_can_only_view_withdrawn_request(self):
        admin = User.objects.create_superuser(
            username="withdrawn-admin",
            email="withdrawn-admin@hua.gr",
            password="Password123!!",
        )
        request_obj = self.create_request(self.student, self.course1, "Withdrawn admin request")
        request_obj.status = CourseRecognitionRequest.WITHDRAWN
        request_obj.withdrawn_by = admin
        request_obj.withdrawal_reason = "Admin should see this withdrawal reason"
        request_obj.save(update_fields=["status", "withdrawn_by", "withdrawal_reason", "updated_at"])

        self.client.force_login(admin)
        inactive_filter_url = f"{reverse('course_recognition:admin_requests')}?status=inactive"
        request_list = self.client.get(inactive_filter_url)
        self.assertContains(
            request_list,
            (
                reverse("course_recognition:admin_request_detail", args=(request_obj.id,))
                + "?next=/el/admin/course-recognition/%3Fstatus%3Dinactive"
            ),
        )
        self.assertNotContains(
            request_list,
            reverse("course_recognition:admin_request_update", args=(request_obj.id,)),
        )
        detail = self.client.get(reverse("course_recognition:admin_request_detail", args=(request_obj.id,)))
        self.assertContains(detail, "Admin should see this withdrawal reason")
        self.assertContains(detail, admin.username)
        self.assertRedirects(
            self.client.get(reverse("course_recognition:admin_request_update", args=(request_obj.id,))),
            (
                reverse("course_recognition:admin_request_detail", args=(request_obj.id,))
                + "?next=%2Fel%2Fadmin%2Fcourse-recognition%2F"
            ),
        )

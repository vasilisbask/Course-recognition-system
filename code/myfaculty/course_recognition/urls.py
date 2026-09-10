from django.urls import path

from . import views


app_name = "course_recognition"

urlpatterns = [
    path(
        "student/course-recognition/course-autocomplete/",
        views.StudentCourseAutocomplete.as_view(),
        name="student_course_autocomplete",
    ),
    path("student/course-recognition/new/", views.student_request_create, name="student_request_create"),
    path("student/course-recognition/<int:pk>/", views.student_request_detail, name="student_request_detail"),
    path("student/course-recognition/<int:pk>/edit/", views.student_request_update, name="student_request_update"),
    path("professor/course-recognition/<int:pk>/recommendation/", views.professor_recommendation, name="professor_recommendation"),
    path(
        "secretariat/course-recognition/course-autocomplete/",
        views.SecretariatCourseAutocomplete.as_view(),
        name="secretariat_course_autocomplete",
    ),
    path(
        "secretariat/course-recognition/professor-autocomplete/",
        views.ProfessorAutocomplete.as_view(),
        name="professor_autocomplete",
    ),
    path("secretariat/course-recognition/", views.secretariat_requests, name="secretariat_requests"),
    path("secretariat/course-recognition/export.xlsx", views.secretariat_export_xlsx, name="secretariat_export_xlsx"),
    path("secretariat/course-recognition/course-assignment/", views.secretariat_course_assignment, name="secretariat_course_assignment"),
    path("secretariat/course-recognition/<int:pk>/protocol/", views.secretariat_protocol, name="secretariat_protocol"),
    path("secretariat/course-recognition/<int:pk>/recommendation/", views.secretariat_recommendation, name="secretariat_recommendation"),
    path("secretariat/course-recognition/<int:pk>/recommendation/accept/", views.secretariat_accept_recommendation, name="secretariat_accept_recommendation"),
    path("secretariat/course-recognition/<int:pk>/recommendation/reject/", views.secretariat_reject_recommendation, name="secretariat_reject_recommendation"),
    path("secretariat/course-recognition/<int:pk>/withdraw/", views.secretariat_withdraw, name="secretariat_withdraw"),
    path("secretariat/course-recognition/<int:pk>/restore/", views.secretariat_restore, name="secretariat_restore"),
    path(
        "admin/course-recognition/<int:pk>/course-autocomplete/",
        views.AdminCourseAutocomplete.as_view(),
        name="admin_course_autocomplete",
    ),
    path("admin/course-recognition/", views.admin_requests, name="admin_requests"),
    path("admin/course-recognition/export.xlsx", views.admin_export_xlsx, name="admin_export_xlsx"),
    path("admin/course-recognition/<int:pk>/", views.admin_request_detail, name="admin_request_detail"),
    path("admin/course-recognition/<int:pk>/edit/", views.admin_request_update, name="admin_request_update"),
    path("admin/course-recognition/<int:pk>/protocol/", views.admin_protocol, name="admin_protocol"),
    path("admin/course-recognition/<int:pk>/recommendation/", views.admin_recommendation, name="admin_recommendation"),
    path("admin/course-recognition/<int:pk>/recommendation/accept/", views.admin_accept_recommendation, name="admin_accept_recommendation"),
    path("admin/course-recognition/<int:pk>/recommendation/reject/", views.admin_reject_recommendation, name="admin_reject_recommendation"),
    path("admin/course-recognition/<int:pk>/withdraw/", views.admin_withdraw, name="admin_withdraw"),
    path("admin/course-recognition/<int:pk>/restore/", views.admin_restore, name="admin_restore"),
]

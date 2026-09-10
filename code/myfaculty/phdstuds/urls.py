from django.urls import path
from . import views

app_name = 'phdstuds'
urlpatterns = [    

    # URLs for Secretary CRUD for Thesis
    path('sec/phdthesis/new', views.SecCreatePhDThesis.as_view(), name='sec_create_phd_thesis'),
    path('sec/phdthesis/<int:pk>', views.SecUpdatePhDThesis.as_view(), name='sec_update_thesis'),
    path('sec/phdtheses/', views.SecListPhDThesis.as_view(), name="sec_list_theses"),
    path('sec/phdthesis/<int:pk>/delete', views.SecDeletePhDThesis.as_view(), name='sec_delete_thesis'),
    
    # URLs for Secretary CRUD for Student
    path('sec/phdstudent/new', views.SecCreatePhDStudent.as_view(), name='sec_create_phd_student'),
    path('sec/phdstudent/<int:pk>', views.SecUpdatePhDStudent.as_view(), name='sec_update_phd_student'),
    path('sec/', views.SecListPhDStudent.as_view(), name="sec_list_phd_students"),
    path('sec/phdstudent/<int:pk>/delete', views.SecDeletePhDStudent.as_view(), name='sec_delete_phd_student'),
    path('sec/phdstudent/<int:pk>/overview', views.SecStudentOverviewList.as_view(), name='sec_overview_phd_student'),
    
    # URLs for Secretary U for PersonalInfo
    path('sec/phdstudent/<int:pk>/pi', views.SecUpdatePersonalInfo.as_view(), name='sec_update_phd_student_pi'),

    # URLs for Secretary CRUD for Progress Report
    path('sec/progress/new', views.SecCreateProgress.as_view(), name='sec_create_progress'),
    path('sec/progress/<int:pk>', views.SecUpdateProgress.as_view(), name='sec_update_progress'),
    path('sec/progress/', views.SecListProgress.as_view(), name="sec_list_progress"),
    path('sec/progress/<int:pk>/delete', views.SecDeleteProgress.as_view(), name='sec_delete_progress'),

    # URLs for Secretary CRUD for Progress Report
    path('sec/recommendation/new', views.SecCreateRecommendation.as_view(), name='sec_create_recommendation'),
    path('sec/recommendation/<int:pk>', views.SecUpdateRecommendation.as_view(), name='sec_update_recommendation'),
    path('sec/recommendations/', views.SecListRecommendation.as_view(), name="sec_list_recommendations"),
    path('sec/recommendation/<int:pk>/delete', views.SecDeleteRecommendation.as_view(), name='sec_delete_recommendation'),

    # URLs for Secretary CRUD for Journal Publications
    path('sec/journal/new', views.SecCreateJournal.as_view(), name='sec_create_journal'),
    path('sec/journal/<int:pk>', views.SecUpdateJournal.as_view(), name='sec_update_journal'),
    path('sec/journals/', views.SecListJournal.as_view(), name="sec_list_journals"),
    path('sec/journal/<int:pk>/delete', views.SecDeleteJournal.as_view(), name='sec_delete_journal'),

    # URLs for Secretary CRUD for Conference Publications
    path('sec/conference/new', views.SecCreateConference.as_view(), name='sec_create_conference'),
    path('sec/conference/<int:pk>', views.SecUpdateConference.as_view(), name='sec_update_conference'),
    path('sec/conferences/', views.SecListConference.as_view(), name="sec_list_conferences"),
    path('sec/conference/<int:pk>/delete', views.SecDeleteConference.as_view(), name='sec_delete_conference'),

    # URLs for Secretary CRUD for TeachingTask Publications
    path('sec/teachingtask/new', views.SecCreateTeachingTask.as_view(), name='sec_create_teachingtask'),
    path('sec/teachingtask/<int:pk>', views.SecUpdateTeachingTask.as_view(), name='sec_update_teachingtask'),
    path('sec/teachingtasks/', views.SecListTeachingTask.as_view(), name="sec_list_teachingtasks"),
    path('sec/teachingtask/<int:pk>/delete', views.SecDeleteTeachingTask.as_view(), name='sec_delete_teachingtask'),

    # URLs for Secretary autocomplete
    path('sec/phdthesis/autocomplete', views.SecThesisAutoComplete.as_view(), name='sec-phd-thesis-autocomplete'),
    
    # URLs for Staff Member
    path('staff/', views.StaffListPhDThesis.as_view(), name="staff_list_theses"),
    path('staff/phdthesis/<int:pk>', views.StaffUpdatePhDThesis.as_view(), name='staff_update_thesis'),
    path('staff/phdstudent/<int:pk>/overview', views.StaffStudentOverviewList.as_view(), name='staff_overview_phd_student'),
    path('staff/progress/<int:pk>', views.StaffUpdateProgress.as_view(), name='staff_update_progress'),
    path('staff/recommendation/<int:pk>', views.StaffUpdateRecommendation.as_view(), name='staff_update_recommendation'),    
    path('staff/journal/<int:pk>', views.StaffUpdateJournal.as_view(), name='staff_update_journal'),
    path('staff/conference/<int:pk>', views.StaffUpdateConference.as_view(), name='staff_update_conference'),
    path('staff/teachingtask/<int:pk>', views.StaffUpdateTeachingTask.as_view(), name='staff_update_teachingtask'),
    path('staff/recommendation/<int:pk>/create', views.StaffCreateRecommendation.as_view(), name='staff_create_recommendation'),
    path('staff/recommendation/create', views.StaffCreateRecommendationGeneric.as_view(), name='staff_create_recommendation_generic'),    
    path('staff/recommendations', views.StaffListRecommendations.as_view(), name='staff_list_recommendations'),
    
    # URLS for Students

    # URLs for Thesis
    path('stud/', views.StudentOverviewList.as_view(), name='stud_overview'),
        
    path('stud/phdstudent/pi', views.StudentUpdate.as_view(), name='stud_update_phd_student_pi'),

    path('stud/progress/new', views.StudentCreateProgress.as_view(), name='stud_create_progress'),
    path('stud/progress/<int:pk>', views.StudentUpdateProgress.as_view(), name='stud_update_progress'),
    
    path('stud/recommendation/<int:pk>', views.StudentUpdateRecommendation.as_view(), name='stud_update_recommendation'),

    path('stud/journal/new', views.StudentCreateJournal.as_view(), name='stud_create_journal'),
    path('stud/journal/<int:pk>', views.StudentUpdateJournal.as_view(), name='stud_update_journal'),
    path('stud/journal/<int:pk>/delete', views.StudentDeleteJournal.as_view(), name='stud_delete_journal'),

    path('stud/conference/new', views.StudentCreateConference.as_view(), name='stud_create_conference'),
    path('stud/conference/<int:pk>', views.StudentUpdateConference.as_view(), name='stud_update_conference'),
    path('stud/conference/<int:pk>/delete', views.StudentDeleteConference.as_view(), name='stud_delete_conference'),

    path('stud/teachingtask/new', views.StudentCreateTeachingTask.as_view(), name='stud_create_teachingtask'),
    path('stud/teachingtask/<int:pk>', views.StudentUpdateTeachingTask.as_view(), name='stud_update_teachingtask'),
    path('stud/teachingtask/<int:pk>/delete', views.StudentDeleteTeachingTask.as_view(), name='stud_delete_teachingtask'),
    path('stud/pi', views.StudentPI.as_view(), name='stud_update_pi'),

    
 ]
from django.urls import path, include
from .views import StaffMemberApiView, AssociateApiView, AttendanceApiView, CourseApiView
from rest_framework.authtoken import views

urlpatterns= [
    path('staff/', StaffMemberApiView.as_view()),
    path('associates/', AssociateApiView.as_view()),
    path('attendances/', AttendanceApiView.as_view()),
    path('course/', CourseApiView.as_view()),
    
    path('auth/', views.obtain_auth_token)
]
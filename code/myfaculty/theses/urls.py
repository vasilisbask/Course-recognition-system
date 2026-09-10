from django.urls import path

from . import views

app_name = 'theses'
urlpatterns = [    
    path('sec', views.sec_list, name='sec_list'),
    path('sec/program/<int:id>', views.sec_list_program, name='sec_list_program'),    
    path('sec/<int:pk>', views.sec_edit.as_view(), name='sec_edit'),
    path('sec/new', views.sec_create.as_view(), name='sec_create'),
    path('sec/<int:pk>/delete', views.sec_delete, name='sec_delete'),
    path('sec/<int:pk>/cancel', views.cancel_assignment, name='sec_cancel'),    
    path('staff', views.staff_list, name='staff_list'),
    path('staff/<int:pk>', views.staff_edit.as_view(), name='staff_edit'),
    path('staff/new', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/delete', views.staff_delete, name='staff_delete'),
    path('public/<int:c>', views.public_list, name='public_list'),
    path('public/<int:pk>/detail', views.public_detail, name='public_detail'),
    path('sec/export/nonga', views.export_non_ga, name='export_non_ga'),
    path('sec/export/graded/<int:id>', views.export_graded_program, name='export_graded_program'),
    path('sec/export/noga/<int:id>', views.export_assigned_noga, name='export_assigned_noga'),
    path('sec/export/ga/<int:id>', views.export_assigned_ga, name='export_assigned_ga'),
    path('sec/export/unassigned/<int:id>', views.export_unassigned, name='export_unassigned'),
    path('sec/filter/<int:program_id>/<str:status>', views.sec_filter, name='sec_filter'),
    path('sec/export/filter/<int:program_id>/<str:status>', views.sec_filter_export, name='sec_filter_export'),    
    path('student/dashboard', views.student_dashboard, name='student_dashboard'),
    path('student/declare/<int:pk>', views.declare_thesis, name='declare_thesis'),
    path('student/upload/<str:doc_type>/<int:pk>', views.upload_document, name='upload_document'),
    path('student/download/<str:doc_type>/<int:pk>', views.get_document, name='get_document'),
    path('student/request/extension/<int:pk>', views.ask_for_extension, name='ask_for_extension')
 ]
from django.urls import path

from . import views

app_name = 'projects'
urlpatterns = [    
    path('sec/projects', views.sec_list_projects.as_view(), name='sec_list_projects'),
    path('sec/projects/<int:pk>', views.sec_edit_project.as_view(), name='sec_edit_project'),
    path('sec/projects/new', views.sec_create_project.as_view(), name='sec_create_project'),
    path('sec/projects/<int:pk>/delete', views.delete_project, name='delete_project'),
    path('sec/projects/export/<int:pk>', views.export_project_approval, name='export_project_aproval'),    
    path('staff/projects', views.staff_list_projects.as_view(), name='staff_list_projects'),
    path('staff/projects/<int:pk>', views.staff_edit_project.as_view(), name='staff_edit_project'),
    path('staff/projects/new', views.staff_create_project, name='staff_create_project'),
    path('staff/projects/<int:pk>/delete', views.staff_delete_project, name='staff_delete_project'),
    path('sec/export', views.export, name='export')
    
 ]
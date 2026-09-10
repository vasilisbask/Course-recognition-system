from django.urls import path

from . import views

app_name = 'timesheets'
urlpatterns = [    
    path('sec', views.sec_list.as_view(), name='sec_list'),
    path('sec/<int:pk>', views.sec_edit.as_view(), name='sec_edit'),
    path('sec/new', views.sec_create.as_view(), name='sec_create'),
    path('sec/<int:pk>/delete', views.sec_delete, name='sec_delete'),
    path('staff', views.staff_list.as_view(), name='staff_list'),
    path('staff/<int:pk>', views.staff_edit.as_view(), name='staff_edit'),
    path('staff/new', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/delete', views.staff_delete, name='staff_delete'),
    
    
 ]
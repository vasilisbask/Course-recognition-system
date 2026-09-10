from django.urls import path

from . import views

app_name = 'leaves'
urlpatterns = [    
    path('sec/leaves', views.sec_list_leaves.as_view(), name='sec_list_leaves'),
    path('sec/leaves/<int:pk>', views.sec_edit_leave.as_view(), name='sec_edit_leave'),
    path('sec/leaves/new', views.sec_create_leave.as_view(), name='sec_create_leave'),
    path('sec/leaves/<int:pk>/delete', views.delete_leave, name='delete_leave'),
    path('sec/leaves/export/<int:pk>', views.export_leave_approval, name='export_leave_aproval'),    
    path('staff/leaves', views.staff_list_leaves.as_view(), name='staff_list_leaves'),
    path('staff/leaves/<int:pk>', views.staff_edit_leave.as_view(), name='staff_edit_leave'),
    path('staff/leaves/new', views.staff_create_leave, name='staff_create_leave'),
    path('staff/leaves/<int:pk>/delete', views.staff_delete_leave, name='staff_delete_leave'),
    
    
 ]
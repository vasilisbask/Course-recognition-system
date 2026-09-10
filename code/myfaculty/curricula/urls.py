from django.urls import path

from . import views

app_name = 'curricula'
urlpatterns = [    
    path('sec/courses', views.list_course, name='list_courses'),
    path('sec/program/<int:pk>', views.list_program, name='list_program'),
    path('sec/program/active/<int:pk>', views.list_program_active, name='list_program_active'),
    path('sec/program/inactive/<int:pk>', views.list_program_inactive, name='list_program_inactive'),    
    path('sec/course/<int:pk>', views.edit_course.as_view(), name='edit_course'),
    path('sec/course/<int:pg>/<int:pk>', views.edit_program_course.as_view(), name='edit_program_course'),        
    path('sec/course/<int:pk>/delete', views.delete_course, name='delete_course'),
    path('export/course/gr/<int:pk>',views.export_gr, name='export_course_gr'),
    path('export/course/en/<int:pk>',views.export_en, name='export_course_en'),    
    path('staff/courses', views.staff_list_courses.as_view(), name='staff_list_course'),
    path('staff/course/<int:pk>', views.staff_edit_course.as_view(), name='staff_edit_course'),
    path('public/courses/<int:pk>', views.public_list_courses.as_view(), name='public_list_course'),
    path('public/gr/<int:pk>', views.public_list_courses2, name='public_list_course2'),
    path('public/en/<int:pk>', views.public_list_courses2_en, name='public_list_course2_en'),
    path('public/course/<int:pk>', views.public_detail_course.as_view(), name='public_detail_course'),
    path('public/course/en/<int:pk>', views.public_detail_course_en.as_view(), name='public_detail_course_en'),
#    path('sec/course/<int:pk>/delete', views.delete_associate, name='delete_course'),
    path('sec/course/new', views.create_course.as_view(), name='create_course'),
    path('sec/program/export/<int:program_code>', views.export_csv,name='export_program'), 
    path('sec/program/export/en/<int:pk>', views.export_all_en,name='export_all_en'), 
    path('sec/program/export/gr/<int:pk>', views.export_all_gr,name='export_all_gr') 
       
]
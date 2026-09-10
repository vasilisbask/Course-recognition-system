from django.urls import path

from . import views

app_name = 'phdapplications'
urlpatterns = [    

    # # Secretary dahboard
    path('sec/dashboard', views.sec_call_list, name='sec_dashboard'),

    # # URLs for Secretary CRUD for calls
     
    # path('sec/call/delete/<int:pk>', views.sec_call_delete, name='sec_call_delete'),

    # # URLs for Secretary Applications
    # path('sec/call/<int:pk>', views.sec_call_applicant_list.as_view(), name='sec_call_applicant_list'),

    # # URLs for Secretary CRUD for Doctorate Applicants
    # path('sec/applicants', views.sec_applicant_list.as_view(), name='sec_applicant_list'),
    # path('sec/applicant/<int:pk>', views.sec_applicant_edit.as_view(), name='sec_applicant_edit'),
    # path('sec/applicant/new', views.sec_applicant_create.as_view(), name='sec_applicant_create'),
    # path('sec/applicant/delete/<int:pk>', views.sec_applicant_delete, name='sec_applicant_delete'),
    # path('sec/application/delete/<int:call_id>/<int:pk>', views.sec_delete_application, name='sec_delete_application'),

    # # # URLs for Doctoral Application (Secretary Role) 
    # # path('sec/applications/<int:call_id>', views.sec_application_list.as_view(), name='sec_application_list'),
    
    # # Doctoral Condidate pages
    path('dashboard/', views.dashboard, name='applicant_dashboard'),
    # path('create/profile/', views.create_profile.as_view(), name='create_profile'),
    # path('update/profile/', views.update_profile.as_view(), name='update_profile'),
    # path('calls/', views.applicant_call_list.as_view(), name='applicant_call_list'),
    path('call/<int:pk>', views.view_call.as_view(), name='view_call'),
    
    # path('applicant/list/<obj_type>', views.applicant_obj_list, name='applicant_obj_list'),
    # path('applicant/detail/<str:obj_type>/<int:obj_id>',views.applicant_obj_detail, name = 'applicant_obj_detail'),
    # path('applicant/delete/<str:obj_type>/<int:pk>', views.applicant_obj_delete, name = 'applicant_obj_delete'),
    # path('applicant/create/<str:obj_type>', views.applicant_obj_create, name = 'applicant_obj_create'),
    path('applicant/degree/create/<int:app_pk>', views.create_degree.as_view(), name = 'applicant_create_degree'),
    path('applicant/degree/<int:pk>', views.update_degree.as_view(), name = 'applicant_update_degree'),
    path('applicant/degree/<int:pk>/delete', views.candidate_delete_degree.as_view(), name = 'applicant_delete_degree'),

    path('applicant/journal/create/<int:app_pk>', views.create_journal.as_view(), name = 'applicant_create_journal'),
    path('applicant/journal/<int:pk>', views.update_journal.as_view(), name = 'applicant_update_journal'),
    path('applicant/journal/<int:pk>/delete', views.candidate_delete_journal.as_view(), name = 'applicant_delete_journal'),

    path('applicant/conference/create/<int:app_pk>', views.create_conference.as_view(), name = 'applicant_create_conference'),
    path('applicant/conference/<int:pk>', views.update_conference.as_view(), name = 'applicant_update_conference'),
    path('applicant/conference/<int:pk>/delete', views.candidate_delete_conference.as_view(), name = 'applicant_delete_conference'),

    path('applicant/workexp/create/<int:app_pk>', views.create_workexp.as_view(), name = 'applicant_create_workexp'),
    path('applicant/workexp/<int:pk>', views.update_workexp.as_view(), name = 'applicant_update_workexp'),
    path('applicant/workexp/<int:pk>/delete', views.candidate_delete_experience.as_view(), name = 'applicant_delete_experience'),

    path('applicant/contact/create/<int:app_pk>', views.create_contact.as_view(), name = 'applicant_create_contact'),
    path('applicant/contact/<int:pk>', views.update_contact.as_view(), name = 'applicant_update_contact'),
    path('applicant/contact/<int:pk>/delete', views.candidate_delete_contact.as_view(), name = 'applicant_delete_contact'),
    path('applicant/contacts/<int:app_pk>', views.list_contacts, name='applicant_list_contacts'),

#    path('degree/', views.applicant_degree_list.as_view(), name='applicant_degree_list'),
    # path('degree/<int:pk>', views.applicant_degree_edit.as_view(), name='applicant_degree_edit'),
    # path('degree/create', views.applicant_degree_create.as_view(), name='applicant_degree_create'),
    # path('degree/<int:pk>/delete', views.applicant_degree_delete, name='applicant_degree_delete'),

    # # path('publications/', views.applicant_publication_list.as_view(), name='applicant_publication_list'),
    # # path('journal/<int:pk>', views.applicant_journal_edit.as_view(), name='applicant_journal_edit'),
    # # path('journal/create', views.applicant_journal_create.as_view(), name='applicant_journal_create'),
    # # path('journal/<int:pk>/delete', views.applicant_journal_delete, name='applicant_journal_delete'),

    # # path('conference/<int:pk>', views.applicant_conference_edit.as_view(), name='applicant_conference_edit'),
    # # path('conference/create', views.applicant_conference_create.as_view(), name='applicant_conference_create'),
    # # path('conference/<int:pk>/delete', views.applicant_conference_delete, name='applicant_conference_delete'),

    # # path('experience/', views.applicant_experience_list.as_view(), name='applicant_experience_list'),
    # # path('experience/<int:pk>', views.applicant_experience_edit.as_view(), name='applicant_experience_edit'),
    # # path('experience/create', views.applicant_experience_create.as_view(), name='applicant_experience_create'),
    # # path('experience/<int:pk>/delete', views.applicant_experience_delete, name='applicant_experience_delete'),

    # # path('contact/', views.applicant_contact_list.as_view(), name='applicant_contact_list'),
    # # path('contact/<int:pk>', views.applicant_contact_edit.as_view(), name='applicant_contact_edit'),
    # # path('contact/create', views.applicant_contact_create.as_view(), name='applicant_contact_create'),
    # # path('contact/<int:pk>/delete', views.applicant_contact_delete, name='applicant_contact_delete'),

    path('apply/<int:pk>', views.apply, name='apply'),
    path('application/main/<int:pk>', views.application_main.as_view(), name='application_main'),        
    path('application/extra/info/<int:pk>', views.apply_extra_info, name='application_extra'),
    path('pi/<int:pk>', views.update_pi.as_view(), name='update_pi'),
    path('delete/<int:pk>', views.candidate_delete_application.as_view(), name='delete'), 
    path('submit/<int:pk>', views.submit, name='submit'),
    path('reference/letter/<str:token>', views.reference_letter, name='reference_letter'),

    path('rev/pi/<int:pk>', views.rev_view_pi.as_view(), name = 'rev_update_pi'),
    path('rev/degree/<int:pk>', views.rev_view_degree.as_view(), name = 'rev_update_degree'),
    path('rev/journal/<int:pk>', views.rev_view_journal.as_view(), name = 'rev_update_journal'),
    path('rev/conference/<int:pk>', views.rev_view_conference.as_view(), name = 'rev_update_conference'),
    path('rev/workexp/<int:pk>', views.rev_view_experience.as_view(), name = 'rev_update_workexp'),
    path('rev/letter/<int:pk>', views.rev_view_letter.as_view(), name = 'rev_update_letter'),
    path('rev/letters/<int:pk>', views.rev_list_letters, name = 'rev_list_letters'),    
    path('rev/applications/<int:pk>', views.rev_applications, name = 'rev_list_applications'),
    path('rev/application/<int:pk>', views.rev_application, name = 'rev_application'),
    path('rev/', views.rev_dashboard, name = 'rev_dashboard'),
    path('rev/application/main/<int:pk>', views.rev_application_main.as_view(), name='rev_application_main'),        
    path('rev/application/extra/<int:pk>', views.rev_apply_extra_info, name='rev_application_extra'),        

    path('sec/calls', views.sec_call_list, name='sec_call_list'),
    path('sec/call/edit/<int:pk>', views.sec_call_update.as_view(), name='sec_call_update'),
    path('sec/call/new', views.sec_call_create.as_view(), name='sec_call_create'),    
    path('sec/pi/<int:pk>', views.sec_view_pi.as_view(), name = 'sec_update_pi'),    
    path('sec/degree/<int:pk>', views.sec_view_degree.as_view(), name = 'sec_update_degree'),
    path('sec/degree/<int:pk>/delete', views.sec_delete_degree.as_view(), name = 'sec_delete_degree'),
    
    path('sec/journal/<int:pk>', views.sec_view_journal.as_view(), name = 'sec_update_journal'),
    path('sec/journal/<int:pk>/delete', views.sec_delete_journal.as_view(), name = 'sec_delete_journal'),
    
    path('sec/conference/<int:pk>', views.sec_view_conference.as_view(), name = 'sec_update_conference'),
    path('sec/conference/<int:pk>/delete', views.sec_delete_conference.as_view(), name = 'sec_delete_conference'),
    
    path('sec/workexp/<int:pk>', views.sec_view_experience.as_view(), name = 'sec_update_experience'),
    path('sec/workexp/<int:pk>/delete', views.sec_delete_experience.as_view(), name = 'sec_delete_experience'),
    
    path('sec/letter/<int:pk>', views.sec_view_letter.as_view(), name = 'sec_update_letter'),
    path('sec/letter/<int:pk>/delete', views.sec_delete_letter.as_view(), name = 'sec_delete_letter'),    
    path('sec/letters/<int:pk>', views.sec_list_letters, name = 'sec_list_letters'),    
    path('sec/applications/<int:pk>', views.sec_applications, name = 'sec_list_applications'),
    path('sec/application/<int:pk>', views.sec_application, name = 'sec_application'),
    path('sec/application/<int:pk>/delete', views.sec_delete_application.as_view(), name = 'sec_delete_application'),
    
    path('sec/', views.sec_call_list, name = 'sec_dashboard'),
    path('sec/application/main/<int:pk>', views.sec_application_main.as_view(), name='sec_application_main'),        
    path('sec/application/extra/<int:pk>', views.sec_apply_extra_info, name='sec_application_extra'),        
    path('sec/application/export/<int:pk>', views.export_application_pdf, name='export_application_pdf'),        

    
    # path('contact-autocomplete/', views.ReferenceContactAutoComplete.as_view(), name='contact-autocomplete'),
    
    # path('<str:role>/application/summary/<int:pk>', views.application_summary, name='application_summary'),
  
    # path('reviewer/<str:obj_type>/<int:application_id>/<int:obj_id>', views.reviewer_obj_details, name='reviewer_obj_details'),
    # path('reviewer/call/<int:pk>', views.reviewer_call, name = 'reviewer_call'),
    # path('reviewer/dashboard/', views.reviewer_dashboard, name = 'reviewer_dashboard'),
    
    # path('sec/application/detail/<str:obj_type>/<int:application_id>/<int:obj_id>', views.sec_obj_application_details, name='sec_obj_application_details'),
    # path('sec/application/detail/<int:id>', views.sec_edit_application, name='sec_edit_application'),
  
    # path('sec/create/<str:obj_type>/<int:applicant_id>', views.sec_create, name='sec_create'),
    # path('sec/list/<str:obj_type>/<int:applicant_id>', views.sec_list, name = 'sec_list'),
    # path('sec/detail/<str:obj_type>/<int:applicant_id>/<int:obj_id>',views.sec_detail, name = 'sec_detail'),
    # path('sec/application/<application_id>/reference/create', views.sec_ref_create, name = 'sec_ref_create'),
    # path('sec/delete/<str:obj_type>/<int:applicant_id>/<int:pk>', views.sec_delete, name = 'sec_delete'),
    # path('sec/export/<int:pk>', views.export_summary, name='export_summary'),

 ]
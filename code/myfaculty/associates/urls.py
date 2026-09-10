from django.urls import path
from . import views

app_name = 'associates'
urlpatterns = [
    path('attendances', views.sec_list_attendances.as_view(), name='sec_list_attendances'),
    path('attendances/<int:pk>', views.sec_list_attendances.as_view(), name='sec_list_attendances'),
    path('cards', views.sec_list_cards.as_view(), name='sec_list_cards'),
    path('export', views.export_attendances, name='export'),
]
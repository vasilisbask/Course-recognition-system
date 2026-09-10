from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import Attendance
from myprofile.models import Associate
from .models import Card

from myprofile.checks import is_secreteriat
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
import csv
from django.forms.models import model_to_dict
from .forms import export_form

# Create your views here.

class sec_list_attendances(UserPassesTestMixin, LoginRequiredMixin, generic.ListView):
    
    template_name = "associates/list_attendances.html"
    context_object_name = "attendances"


    def test_func(self):
        return is_secreteriat(self.request.user)


    def get_queryset(self):
        if 'pk' in self.kwargs:
            pk = self.kwargs.get('pk')
            associate = get_object_or_404(Associate, pk = pk)
            return Attendance.objects.filter(associate = associate)[:100]
        else:
            return Attendance.objects.all()[:100]
        
class sec_list_cards(UserPassesTestMixin, LoginRequiredMixin, generic.ListView):
    
    template_name = "associates/list_cards.html"
    context_object_name = "cards"


    def test_func(self):
        return is_secreteriat(self.request.user)


    def get_queryset(self):
        return Card.objects.all()[:100]
        
def export_attendances(request):
    
    if request.method == 'POST':
        form = export_form(request.POST)

        if form.is_valid():
            associate = form.cleaned_data.get('associate')
            reference_year = form.cleaned_data.get('reference_year')

            if not associate and not reference_year:
                attendances = Attendance.objects.all()
            elif associate:                                
                attendances = Attendance.objects.filter(associate=associate)
            
            if reference_year:
                attendances = attendances.filter(updated_year__year = reference_year)

            
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="export.csv"'},
            )

            writer = csv.writer(response, delimiter=';', quoting = csv.QUOTE_ALL)        
            for i, attendance in enumerate(attendances):
                
                obj = model_to_dict(attendance)
                obj['associate'] = attendance.associate.display_name
                if i==0:
                    writer.writerow(obj.keys())
                l = [obj[k] for k in obj.keys()]
                writer.writerow(l)

            return response
        else:
            return render(request, 'associates/export.html', 
                          {'form' : form})
    else:
        form = export_form()
        return render(request, 'associates/export.html', 
                          {'form' : form})
    
    
    

from django.forms.models import model_to_dict
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from myprofile.checks import is_staff_member, is_secreteriat
from .models import Project
from myprofile.models import StaffMember
from .forms import SecCreateProjectForm, SecUpdateProjectForm, StaffCreateProjectForm, StaffUpdateProjectForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse_lazy
from export.models import DocumentTemplate
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
import csv

# Create your views here.

class sec_list_projects(UserPassesTestMixin, LoginRequiredMixin, generic.ListView):
    
    template_name = "projects/sec_list_projects.html"
    context_object_name = "projects"

    def test_func(self):
        return is_secreteriat(self.request.user)

    def get_queryset(self):
        return Project.objects.order_by('-created_date')

class sec_edit_project(UserPassesTestMixin, LoginRequiredMixin, generic.UpdateView):
    model = Project
    template_name = "projects/sec_edit_project.html"
    form_class = SecUpdateProjectForm
    success_url = reverse_lazy('projects:sec_list_projects')

    def test_func(self):
        return is_secreteriat(self.request.user)
    
class sec_create_project(UserPassesTestMixin, LoginRequiredMixin, generic.CreateView):
    model = Project
    template_name = "projects/sec_edit_project.html"
    form_class = SecCreateProjectForm
    success_url = reverse_lazy('projects:sec_list_projects')

    def test_func(self):
        return is_secreteriat(self.request.user)


@login_required
@user_passes_test(is_secreteriat)    
def delete_project(request, pk):
    obj = get_object_or_404(Project, pk=pk)
    obj.delete()
    return redirect('projects:sec_list_projects')

class staff_list_projects(UserPassesTestMixin, LoginRequiredMixin, generic.ListView):
    
    template_name = "projects/staff_list_projects.html"
    context_object_name = "projects"

    def test_func(self):
        return is_staff_member(self.request.user)

    def get_queryset(self):
        P = get_object_or_404(StaffMember, user = self.request.user)
        return Project.objects.filter(coordinator=P).order_by('-created_date')

class staff_edit_project(UserPassesTestMixin, LoginRequiredMixin, generic.UpdateView):
    model = Project
    template_name = "projects/staff_edit_project.html"
    form_class = StaffUpdateProjectForm
    success_url = reverse_lazy('projects:staff_list_projects')

    def test_func(self):
        obj = self.get_object()        
        return is_staff_member(self.request.user) and (obj.coordinator.user == self.request.user)
    
# class staff_create_project(UserPassesTestMixin, LoginRequiredMixin, generic.CreateView):
#     model = Project
#     template_name = "projects/staff_edit_project.html"
#     form_class = StaffCreateProjectForm
#     success_url = reverse_lazy('projects:staff_list_projects')

#     def get_form(self, *args, **kwargs):
#         form = super().get_form(*args, **kwargs)
#         form.coordinator = get_object_or_404(StaffMember, user=self.request.user)
#         return form
    
#     def test_func(self):
#         return is_staff_member(self.request.user)

@login_required
@user_passes_test(is_staff_member)
def staff_create_project(request):

    coordinator = get_object_or_404(StaffMember, user=request.user)
    if request.method == 'POST':
        form = StaffCreateProjectForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.coordinator = coordinator
            obj.save()
            return redirect('projects:staff_list_projects')
    else:
        form = StaffCreateProjectForm()

    return render(request, 'projects/staff_edit_project.html', {'form' : form})

@login_required
def staff_delete_project(request, pk):
    p = get_object_or_404(StaffMember, user = request.user)
    obj = get_object_or_404(Project, pk=pk, coordinator = p)
    obj.delete()
    return redirect('projects:staff_list_projects')

@login_required
@user_passes_test(is_secreteriat)
def export_project_approval(request, pk):
    d = DocumentTemplate.objects.get(name=settings.PROPOSAL_TEMPLATE)
    p = Project.objects.get(pk = pk)    
    return d.export_file_response(p.approval_dict())

@login_required
@user_passes_test(is_secreteriat)
def export_response(request):
        
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="export.csv"'},
    )

    writer = csv.writer(response, delimiter=';', quoting = csv.QUOTE_ALL)        
    objs = Project.objects.order_by('-created_date')[:100]
    i = 0
    for obj in objs:
        d = {
            'coordinator' : obj.coordinator.display_name,            
            'created_date' : obj.created_date,
            'title' : obj.acronym,
            'abstract' : obj.abstract,
            'call' : obj.call,
            'budget' : obj.budget_total,
            'budget_department' : obj.budget_dep,            
            'thematic_areas' : obj.thematic_areas,
            'funding_rate' : obj.funding_date,
            'partners' : obj.partners,
            'start' : obj.start,
            'duration' : obj.duration,
            'submission_date': obj.submission_date,
            'approved' : obj.approved,
            'submission_approved_ga' : obj.submission_approved_ga,
            'implementation_approved_ga' : obj.implementation_approved_ga,
            'acronym' : obj.acronym
        }
        if i==0:
            writer.writerow(d.keys())
        l = [d[k] for k in d.keys()]
        i += 1
        writer.writerow(l)

    return response

def export(request):
    return export_response(request)



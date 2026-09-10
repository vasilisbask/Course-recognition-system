from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, FileResponse, Http404
from myprofile.checks import is_staff_member, is_secreteriat, is_student
from .models import Thesis, month_to_semester, thesis_to_dict, thesis_filters
from myprofile.models import StaffMember, Student
from curricula.models import StudyProgram
from .forms import SecCreateForm, SecUpdateForm, StaffCreateForm, StaffUpdateForm, PublicDetailForm, StudentReportForm, StudentDocumentForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
import csv
from datetime import datetime
from scopes.utils import get_scoped_object_or_exc

# Create your views here.


@login_required
@user_passes_test(is_student)
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    theses = Thesis.objects.filter(assigned_to=student)
    if theses.count() == 0:
        thesis = None
    else:
        thesis = theses[0]
    return render(request, 'theses/student_thesis_dash.html',
                  context = {'thesis' : thesis})

@login_required
@user_passes_test(is_student)
def declare_thesis(request, pk):
    student = get_object_or_404(Student, user=request.user)
    thesis = get_object_or_404(Thesis, assigned_to=student, declared=False, pk=pk)
    now = datetime.now()
    thesis.declared_date = now
    thesis.declared = True
    thesis.save()
    return redirect('theses:student_dashboard')

@login_required
@user_passes_test(is_student)
def upload_document(request, doc_type, pk):
    student = get_object_or_404(Student, user=request.user)
    thesis = get_object_or_404(Thesis, assigned_to=student, pk=pk, official_date__isnull=False)

    if doc_type == 'report':
        DocForm = StudentReportForm
        if (thesis.report != '') and (not thesis.report):
            raise Http404()
    elif doc_type == 'document':
        DocForm = StudentDocumentForm
        if (thesis.document != '') and (not thesis.document):
            raise Http404()
    else:
        raise Http404()

    if request.method == 'POST':
        form = DocForm(request.POST, request.FILES, instance=thesis)
        if form.is_valid():
            now = datetime.now()
            thesis = form.save(commit=False)
            if doc_type == 'report':
                thesis.report_created = now
            elif doc_type == 'document':
                thesis.document_created = now
            
            thesis.save()            
            return redirect('theses:student_dashboard')        
    else:
        form = DocForm()

    return render(request, 'theses/upload.html', 
                  context = {'form' : form,
                             'message' : 'υποβολή σχεδίου'})    

@login_required
@user_passes_test(is_student)
def get_document(request,doc_type,pk):
    student = get_object_or_404(Student, user=request.user)
    thesis = get_object_or_404(Thesis, declared=True, assigned_to=student, pk=pk, official_date__isnull=False)
    
    if doc_type == 'report':
        if (not thesis.report) or (thesis.report==''):
            raise Http404()
        f = thesis.report.open('rb')
        
    elif doc_type == 'document':
        if (not thesis.document) or (thesis.document==''):
            raise Http404()
        f = thesis.document.open('rb')
    else:
        raise Http404()
        
    return FileResponse(f)

@login_required
@user_passes_test(is_student)
def ask_for_extension(request, pk):
    now = datetime.now()
    student = get_object_or_404(Student, user=request.user)
    thesis = get_object_or_404(Thesis, declared=True, assigned_to=student, pk=pk,extension_requested=False, official_date__isnull=False)
    
    thesis.extension_requested = True
    thesis.extension_requested_date = now
    thesis.save()
    return redirect('theses:student_dashboard')

@login_required
@user_passes_test(is_secreteriat)
def sec_list(request):

    programs = StudyProgram.objects.sc_filter(user=request.user, 
                                              active=True,
                                              has_thesis=True)
    if programs.count() == 0:
        return render(request, 'theses/message.html', 
                      context = {'message' : 'Δεν διαχειρίζεστε κάποιο πρόγραμμα με διπλωματικές εργασίες.'})
        
    return render(request, 'theses/sec_list.html', context = {
      'programs' : programs
    })

@login_required
@user_passes_test(is_secreteriat)
def sec_list_program(request, id):
    user = request.user    
    program = get_scoped_object_or_exc(StudyProgram, 
                                       user=user, 
                                       has_thesis=True,
                                       pk=id)
    theses = Thesis.objects.sc_filter(user = user)

    theses_unassigned = theses.filter(assigned_to__isnull = True, offered_in=program).order_by('updated_date')
    theses_assigned = theses.filter(assigned_to__isnull = False, assigned_to__program=program)

    theses_assigned_grade = theses_assigned.filter(grade_avg__isnull=False).order_by('-updated_date')
    theses_assigned_ga = theses_assigned.filter(assignment_ga__isnull=False,grade_avg__isnull=True).order_by('-updated_date')
    theses_assigned_noga = theses_assigned.filter(assignment_ga__isnull=True).order_by('-updated_date')

    return render(request, 'theses/sec_program_list.html', context = {
      'theses_assigned_grade' : theses_assigned_grade,
      'theses_assigned_ga' : theses_assigned_ga,
      'theses_assigned_noga' : theses_assigned_noga,
      'theses_unassigned' : theses_unassigned,      
      'program' : program
    })

def sec_filter(request, program_id, status):
    next = request.path
    program = get_scoped_object_or_exc(StudyProgram, 
                                       user=request.user, 
                                       has_thesis=True,
                                       pk=program_id)
        
    theses, status_text = thesis_filters(program, request.user, status)
    
    return render(request, 'theses/sec_filtered_list.html', 
                  context = { 'program' : program,
                              'next' : next,
                              'status' : status,
                              'status_text' : status_text,
                              'theses' : theses})

def sec_filter_export(request, program_id, status):
    user = request.user
    program = get_scoped_object_or_exc(StudyProgram, 
                                       user=user, 
                                       has_thesis=True,
                                       pk=program_id)
    
    theses, _ = thesis_filters(program, user, status)
    thesis_dicts = []

    for thesis in theses:
        thesis_dicts.append( thesis_to_dict(thesis) )

    # Create the HTTP response object with CSV headers
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

    # Create CSV writer
    writer = csv.DictWriter(response, quoting=csv.QUOTE_ALL, fieldnames=thesis_dicts[0].keys())
    writer.writeheader()
    writer.writerows(thesis_dicts)

    return response

class sec_edit(UserPassesTestMixin, LoginRequiredMixin, generic.UpdateView):
    model = Thesis
    template_name = "theses/sec_edit.html"
    form_class = SecUpdateForm
    
    def get_success_url(self):        
        next = self.request.GET.get('next')
        if next:
            return next
        else:
            reverse_lazy('theses:sec_list')

    def test_func(self):
        return is_secreteriat(self.request.user)
    
class sec_create(UserPassesTestMixin, LoginRequiredMixin, generic.CreateView):
    model = Thesis
    template_name = "theses/sec_edit.html"
    form_class = SecCreateForm

    def get_success_url(self):        
        next = self.request.GET.get('next')
        if next:
            return next
        else:
            reverse_lazy('theses:sec_list')

    def test_func(self):
        return is_secreteriat(self.request.user)

@login_required
@user_passes_test(is_secreteriat)    
def sec_delete(request, pk):
    obj = get_object_or_404(Thesis, pk=pk)
    obj.delete()
    return redirect('theses:sec_list')


@login_required
@user_passes_test(is_staff_member)
def staff_list(request):
    P = get_object_or_404(StaffMember, user = request.user)
    theses_active = Thesis.objects.filter(supervisor=P, grade_avg__isnull=True, assigned_to__isnull = True,is_offered=True).order_by('-updated_date')
    theses_inactive = Thesis.objects.filter(supervisor=P,is_offered=False).order_by('-updated_date')
    theses_assigned = Thesis.objects.filter(supervisor=P, grade_avg__isnull=True, assigned_to__isnull = False).order_by('-updated_date')
    theses_graded = Thesis.objects.filter(supervisor=P, grade_avg__isnull=False, assigned_to__isnull = False).order_by('-updated_date')
    
    theses_member = Thesis.objects.filter( Q(member1=P) | Q(member2=P) ).order_by('-updated_date')
    return render(request, 'theses/staff_list.html', context={'theses_active' : theses_active,
                                                              'theses_assigned' : theses_assigned,
                                                              'theses_member' : theses_member,
                                                              'theses_inactive' : theses_inactive,
                                                              'theses_graded' : theses_graded})

class staff_edit(UserPassesTestMixin, LoginRequiredMixin, generic.UpdateView):
    model = Thesis
    template_name = "theses/staff_edit.html"
    form_class = StaffUpdateForm
    success_url = reverse_lazy('theses:staff_list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        
        # Changes can not be made if the thesis is assigned 
        P = get_object_or_404(StaffMember, user = self.request.user)
        if form.instance.supervisor == P:
            pass
        elif form.instance.assigned_to or form.instance.member1==P or form.instance.member2==P:
            #form.fields.pop('assigned_to_char')
            for f in form.fields:
                form.fields[f].disabled = True
                
        # Check fields that need to be activated
        if form.instance.supervisor == P:
            form.fields['grade_sup'].disabled = False
        elif form.instance.member1 == P:
            form.fields['grade_member1'].disabled = False
        elif form.instance.member2 == P:
            form.fields['grade_member2'].disabled = False
            
        return form
    
    def test_func(self):
        obj = self.get_object()        
        return is_staff_member(self.request.user) and ( 
                (obj.supervisor.user == self.request.user) 
                or (obj.member1.user == self.request.user)                     
                or (obj.member2.user == self.request.user) )
    
@login_required
@user_passes_test(is_staff_member)
def staff_create(request):
    supervisor = get_object_or_404(StaffMember, user=request.user)
    if request.method == 'POST':
        form = StaffCreateForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.supervisor = supervisor
            obj.save()
            form.save_m2m()
            return redirect('theses:staff_list')
    else:
        form = StaffCreateForm()

    return render(request, 'theses/staff_edit.html', context = {'form' : form})

@login_required
def staff_delete(request, pk):
    p = get_object_or_404(StaffMember, user = request.user)
    obj = get_object_or_404(Thesis, pk=pk, supervisor = p)
    obj.delete()
    return redirect('theses:staff_list')


@login_required
@user_passes_test(is_secreteriat)
def cancel_assignment(request, pk):
    obj = get_object_or_404(Thesis, pk=pk)
    obj.clear_assignment()    
    obj.save()
    return redirect('theses:sec_list')

def public_list(request,c):
    
    P = get_object_or_404(StudyProgram, code_gr=str(c))
    theses = Thesis.objects.filter(is_offered = True, offered_in= P, assigned_to__isnull = True).order_by('-created_date')
    return render(request, 'theses/public_list.html', context={'theses' : theses, 'program' : P})

def public_detail(request,pk):    
    
    thesis = get_object_or_404(Thesis, pk = pk, is_offered=True)
    form = PublicDetailForm(instance=thesis)
    return render(request, 'theses/public_detail.html', context={'form' : form})


def objs_to_csv(objs):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="export.csv"'},
    )

    writer = csv.writer(response, delimiter=';', quoting = csv.QUOTE_ALL)        
    i = 0
    for obj in objs:
        try:
            d = {
                'supervisor_id': obj.supervisor.display_name,
                'member1_id': obj.member1.display_name,
                'member2_id': obj.member2.display_name,
                'title_gr': obj.title_gr,
                'title_en': obj.title_en,
                'abstract': obj.abstract,
                'updated_date': obj.updated_date,
                'created_date': obj.created_date,
                'is_offered': obj.is_offered,
                'assignment_ga': obj.assignment_ga,
                'assignment_date': obj.assignment_date,
                'notes': obj.notes,
                'grade_sup': obj.grade_sup,
                'grade_member1': obj.grade_member1,
                'grade_member2': obj.grade_member2,
                'grade_avg': obj.grade_avg
                }
            if obj.assigned_to:
                d['assigned_to_id'] = obj.assigned_to.display_name
                d['assigned_to_reg_num'] = obj.assigned_to.reg_num
                d['assigned_to_email'] = obj.assigned_to.email
                
            
            if i==0:
                writer.writerow(d.keys())
            l = [d[k] for k in d.keys()]
            i += 1
            writer.writerow(l)
        except AttributeError as e:
            pass

    return response

@login_required
@user_passes_test(is_secreteriat)
def export_non_ga(request):

    objs= Thesis.objects.filter(assigned_to__isnull = False, assignment_ga__isnull = True).order_by('-updated_date')
    return objs_to_csv(objs)

@login_required
@user_passes_test(is_secreteriat)        
def export_graded_program(request, id):

    program = get_object_or_404(StudyProgram, pk = id)
    objs = Thesis.objects.filter(grade_avg__isnull = False, assigned_to__program = program).order_by('-updated_date')
    return objs_to_csv(objs)

@login_required
@user_passes_test(is_secreteriat)        
def export_assigned_ga(request, id):
    program = get_object_or_404(StudyProgram, pk=id)
    theses_assigned = Thesis.objects.filter(assigned_to__isnull = False, assigned_to__program=program)
    objs = theses_assigned.filter(assignment_ga__isnull=False,grade_avg__isnull=True).order_by('-updated_date')
    return objs_to_csv(objs)

@login_required
@user_passes_test(is_secreteriat)        
def export_assigned_noga(request, id):
    program = get_object_or_404(StudyProgram, pk=id)
    theses_assigned = Thesis.objects.filter(assigned_to__isnull = False, assigned_to__program=program)
    objs = theses_assigned.filter(assignment_ga__isnull=True).order_by('-updated_date')
    return objs_to_csv(objs)


@login_required
@user_passes_test(is_secreteriat)        
def export_unassigned(request, id):
    program = get_object_or_404(StudyProgram, pk=id)
    objs = Thesis.objects.filter(assigned_to__isnull = True, offered_in=program).order_by('updated_date')
    return objs_to_csv(objs)

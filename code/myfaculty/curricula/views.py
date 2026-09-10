from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from myprofile.checks import is_staff_member, is_secreteriat
from .models import Course, StudyProgram
from myprofile.models import StaffMember
from .forms import CourseForm, StaffCourseForm, PublicCourseForm, PublicCourseFormEn
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse_lazy
from export.models import DocumentTemplate
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
import csv

# Create your views here.

@login_required
@user_passes_test(is_secreteriat)

def list_course(request):    
    courses = Course.objects.all()
    programs = StudyProgram.objects.filter(active=True).all()
    
    return render(request, 'curricula/sec_list_courses.html', context= {'courses' : courses, 'programs' : programs})

def list_program(request, pk):
    program = get_object_or_404(StudyProgram, pk = pk)
    courses = Course.objects.filter(program=program).order_by('semester')
    return render(request, 'curricula/sec_list_program.html', context= {'courses' : courses, 'program': program})

def list_program_active(request, pk):
    program = get_object_or_404(StudyProgram, pk = pk)
    courses = Course.objects.filter(program=program,active=True).order_by('semester')
    return render(request, 'curricula/sec_list_program.html', context= {'courses' : courses, 'program': program})

def list_program_inactive(request, pk):
    program = get_object_or_404(StudyProgram, pk = pk)
    courses = Course.objects.filter(program=program,active=False).order_by('semester')
    return render(request, 'curricula/sec_list_program.html', context= {'courses' : courses, 'program': program})


class staff_list_courses(UserPassesTestMixin, LoginRequiredMixin, generic.ListView):
    
    template_name = "curricula/list_courses.html"
    context_object_name = "courses"

    def test_func(self):
        return is_staff_member(self.request.user)

    def get_queryset(self):
        p = StaffMember.objects.get(user=self.request.user)
        courses = Course.objects.filter(assigned_to = p)
        return courses

class edit_course(UserPassesTestMixin, LoginRequiredMixin, generic.UpdateView):
    model = Course
    template_name = "curricula/edit_course.html"
    form_class = CourseForm
    success_url = reverse_lazy('curricula:list_courses')
    
    def test_func(self):
        return is_secreteriat(self.request.user)

class edit_program_course(UserPassesTestMixin, LoginRequiredMixin, generic.UpdateView):
    model = Course
    template_name = "curricula/edit_course.html"
    form_class = CourseForm

    def get_success_url(self):
        program_pk = self.kwargs['pg']
        return reverse_lazy('curricula:list_program',args=[program_pk])
     
    def test_func(self):
        return is_secreteriat(self.request.user)
    
class staff_edit_course(UserPassesTestMixin, LoginRequiredMixin, generic.UpdateView):
    model = Course
    template_name = "curricula/edit_course.html"
    form_class = StaffCourseForm
    success_url = reverse_lazy('curricula:staff_list_course')

    def test_func(self):
        p = get_object_or_404(StaffMember, user=self.request.user)
        return p in self.get_object().assigned_to.all()

class create_course(UserPassesTestMixin, LoginRequiredMixin, generic.CreateView):
    model = Course
    template_name = "curricula/edit_course.html"
    form_class = CourseForm
    success_url = reverse_lazy('curricula:list_courses')

    def test_func(self):
        return is_secreteriat(self.request.user)

class public_list_courses(generic.ListView):
    
    template_name = "curricula/public_list_courses.html"
    context_object_name = "courses"

    def get_queryset(self):
        program = get_object_or_404(StudyProgram, id = self.kwargs['pk'])
        return Course.objects.filter(program = program)
    
def public_list_courses2(request, pk):
    program = get_object_or_404(StudyProgram, pk=pk)
    courses = Course.objects.filter(program = program)
    semester_max = max([int(c.semester) for c in courses])
    obl = {}
    elec = {}
    for n in range(semester_max):
      obl[n + 1] = Course.objects.filter(program=program,semester = n + 1, active = True, elective = False).order_by('code_gr')
      elec[n + 1] = Course.objects.filter(program=program,semester = n + 1, active = True, elective = True).order_by('code_gr')

    semesters = [n+1 for n in range(semester_max)]
    return render(request, 'curricula/public_list_courses2.html', context= {'obl' : obl,'elec' : elec, 'semesters' : semesters})

def public_list_courses2_en(request, pk):
    program = get_object_or_404(StudyProgram, pk=pk)
    courses = Course.objects.filter(program = program)
    semester_max = max([int(c.semester) for c in courses])
    obl = {}
    elec = {}
    for n in range(semester_max):
      obl[n + 1] = Course.objects.filter(program=program,semester = n + 1, active = True, elective = False).order_by('code_en')
      elec[n + 1] = Course.objects.filter(program=program,semester = n + 1, active = True, elective = True).order_by('code_en')

    semesters = [n+1 for n in range(semester_max)]
    return render(request, 'curricula/public_list_courses2_en.html', context= {'obl' : obl,'elec' : elec, 'semesters' : semesters})

        

    

class public_detail_course(generic.UpdateView):
    
    model = Course
    template_name = "curricula/public_detail_course.html"
    form_class = PublicCourseForm

class public_detail_course_en(generic.UpdateView):
    
    model = Course
    template_name = "curricula/public_detail_course.html"
    form_class = PublicCourseFormEn

@login_required
def export_gr(request, pk):
    d = DocumentTemplate.objects.get(name=settings.ECTS_GR_TEMPLATE)
    course = Course.objects.get(pk = pk)    
    return d.export_file_response(course.ects_gr_dict())

@login_required
def export_en(request, pk):
    d = DocumentTemplate.objects.get(name=settings.ECTS_EN_TEMPLATE)
    course = Course.objects.get(pk = pk)    
    return d.export_file_response(course.ects_en_dict())


@login_required
@user_passes_test(is_secreteriat)
def export_all_en(request, pk):
    d = DocumentTemplate.objects.get(name=settings.ECTS_EN_TEMPLATE)
    program = StudyProgram.objects.get(pk = pk)
    courses = Course.objects.filter(program = program, active=True).order_by('semester','code_en')
    c_dicts = [c.ects_en_dict() for c in courses]
    return d.export_file_response(c_dicts)

@login_required
@user_passes_test(is_secreteriat)
def export_all_gr(request, pk):
    d = DocumentTemplate.objects.get(name=settings.ECTS_GR_TEMPLATE)
    program = StudyProgram.objects.get(pk = pk)
    courses = Course.objects.filter(program = program, active=True).order_by('semester','code_gr')
    c_dicts = [c.ects_gr_dict() for c in courses]
    return d.export_file_response(c_dicts)

@login_required
@user_passes_test(is_secreteriat)    
def delete_course(request, pk):
    obj = get_object_or_404(Course, pk=pk)
    obj.delete()
    return redirect('myprofile:list_associates')


@login_required
@user_passes_test(is_secreteriat)
def export_response(request, program_code):
        
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="export.csv"'},
    )

    writer = csv.writer(response, delimiter=';', quoting = csv.QUOTE_ALL)        
    objs = Course.objects.filter(program__pk=program_code, active=True).order_by('semester').all()
    i = 0
    for obj in objs:
        d = obj.to_dict()
        if i==0:
            writer.writerow(d.keys())
        l = [d[k] for k in d.keys()]
        i += 1
        writer.writerow(l)

    return response

def export_csv(request, program_code):
    return export_response(request,program_code)


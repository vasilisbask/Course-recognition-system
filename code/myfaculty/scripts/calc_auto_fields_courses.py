from curricula.models import School, Department, StudyProgram, Course
from myprofile.models import StaffMember
from django.forms.models import model_to_dict

SOURCE = 'Προπτυχιακό Πρόγραμμα Σπουδών (Υπό διαμόρφωση)' 

def run():
    program = StudyProgram.objects.get(title_gr = SOURCE)
    courses = Course.objects.filter(program = program)
    print('Number of source courses:',courses.count())
    
    for course in courses:
        course.save()
        print(course.title_gr)




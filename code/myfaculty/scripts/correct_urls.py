from curricula.models import School, Department, StudyProgram, Course
from myprofile.models import StaffMember
from django.forms.models import model_to_dict

SOURCE = 'Προπτυχιακό Πρόγραμμα Σπουδών (Υπό διαμόρφωση)' 

def run():
    program = StudyProgram.objects.get(title_gr = SOURCE)
    courses = Course.objects.filter(program = program)
    print('Number of source courses:',courses.count())
    
    for course in courses:
        if course.url:
            if 'eclass.hua.gr' not in course.url:
                print(course.title_gr, course.url)
                course.url = 'https://eclass.hua.gr'
                course.save()
        else:
            print(course.title_gr, course.url)
            course.url = 'https://eclass.hua.gr'
            course.save()





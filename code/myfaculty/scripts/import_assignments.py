from myprofile.models import Associate, StaffMember
from curricula.models import Course, StudyProgram
import csv

INSTR_FILENAME = 'scripts/insts.csv.tpl'
ASSIGNMENTS = 'scripts/assign.csv.tpl'
instructors = {}
courses_not_found = []
def run():
    P = StudyProgram.objects.get(sis_code = 550)

    courses = Course.objects.all()
    for c in courses:
        c.title_gr = c.title_gr.replace('\n','')
        c.save()

    with open(INSTR_FILENAME, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                instructors[row[0]] = row[1]
            except:
                print('Could not import row: %s' %row)

    print(instructors)

    with open(ASSIGNMENTS, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i > 0:
                course_name = row[2]
                course = Course.objects.filter(title_gr = course_name, program = P)
                if course.count() > 0:
                    course = course[0]
                    assignments = [row[4], row[8], row[12]]
                    print(i, course_name, course, assignments)
                    course.assigned_to.clear()                               
                    for instr in assignments:
                        if instr != '':
                            email = instructors[instr] + '@hua.gr'
                            instructor = StaffMember.objects.filter(email=email)
                            if instructor.count() > 0:
                                course.assigned_to.add(instructor[0])
                    course.save()
                else:
                    print(i, course_name, 'Not Found!')
                    courses_not_found.append(course_name)


    
    print('Courses not found:')
    for c in courses_not_found:
        print(c)

    
            



    




            
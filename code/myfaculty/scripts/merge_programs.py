from curricula.models import StudyProgram
from myprofile.models import StaffMember, Student
from theses.models import Thesis
from django.forms.models import model_to_dict

OLD_PROGRAM = 'Προπτυχιακό Πρόγραμμα Σπουδών (Παλιό)' 
NEW_PROGRAM = 'Προπτυχιακό Πρόγραμμα Σπουδών'

def run():
    old_program = StudyProgram.objects.get(title_gr = OLD_PROGRAM)
    new_program = StudyProgram.objects.get(title_gr = NEW_PROGRAM)
    
    # bring all students to the new program
    students = Student.objects.filter(program=old_program)
    for student in students:
        student.program = new_program
        print(student)
        student.save()

    # bring all offered theses to the new program
    theses = Thesis.objects.filter(offered_in = old_program)
    for thesis in theses:
        thesis.offered_in.remove(old_program)
        thesis.offered_in.add(new_program)
        print(thesis)
        thesis.save()

    # bring all assigned theses to the new program
    theses = Thesis.objects.filter(assigned_program = old_program)

    for thesis in theses:
        thesis.assigned_program = new_program
        print(thesis)
        thesis.save()

    

    





from myprofile.models import Student

def run():
    students = Student.objects.all()
    for student in students:
        print(student)
        student.save()

            
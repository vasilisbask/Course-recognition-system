from myprofile.models import Student
from curricula.models import StudyProgram


def run():
    students = Student.objects.filter(program__isnull=True)
    for student in students:
        print(student.username)
        student.save()
        
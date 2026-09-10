from myprofile.models import Student
from curricula.models import StudyProgram
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import csv
FILENAME = 'students.csv'
# familyName,givenName,studentStatus,username,semester,inscriptionYear,specialty,masterMail,secondaryMail,program

User = get_user_model()

def run():
    with open(FILENAME,'r') as f:
        reader = csv.DictReader(f, delimiter = ',')
        for row in reader:
            print(row)
            username = row['username']
            sis_code = str(row['program'])
            given_name = row['givenName']
            surname = row['familyName']
            semester = row['semester']
            reg_num = username
            email = username + '@' + settings.INTERNAL_DOMAIN
            try:
                program = StudyProgram.objects.get(sis_code = sis_code)
                try:
                    student = Student.objects.get(username=username)
                except ObjectDoesNotExist:
                    student = Student()
                student.username = username
                student.given_name = given_name
                student.surname = surname
                student.semester = semester
                student.reg_num = reg_num
                student.email = email
                student.program = program
                student.save()
            except ObjectDoesNotExist:
                print('Program with code',sis_code, 'does not exist.')




            
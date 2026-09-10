from curricula.models import School, Department, StudyProgram, Course
from myprofile.models import StaffMember
from sis.sis import sis_to_csv

def run():
    sis_to_csv()

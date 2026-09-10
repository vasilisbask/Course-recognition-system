from budi import budiapi
import os
import sys
import django
import traceback
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myfaculty.settings")
django.setup()

from curricula.models import StudyProgram, Department
from myprofile.models import Student, StaffMember, PersonalInfo
from phdstuds.models import PhdThesis, ThesisProgress
from django.core.files import File

correct_dicts = {
    'eliοtou@hua.gr' : 'eliotou@hua.gr'
}

def correct(s):
    if s in correct_dicts:
        return correct_dicts[s]
    else:
        return s

def convert_date(d):
    return datetime.fromisoformat(d).date()

APP_ID = 'app_cb6ba908523b419caf31b44aa97e1c50'
TABLES = {
    'phds' : 'ta_0406b0e66c3d45bf823e14db055099bd',
    'faculty' : 'ta_ddf9e22686314f638721d931c85e1262',
    'reports' : 'ta_b696a4d0c73040299512d6894754cb9e'
}
APP_MAP = {
    'myphd' : APP_ID
}
MASTER_URL = 'https://mydepartment.ditapps.hua.gr'
URL = MASTER_URL + '/api/public/v1'

PROGRAM_TITLE_GR = 'Διδακτορικό Πρόγραμμα Σπουδών'
DEPARTMENT_TITLE_GR = 'Πληροφορικής και Τηλεματικής'

TMP_DEST = '/code/tmp'

def get_file(name, url, output_dir=TMP_DEST):
    r = requests.get(url)
    r.raise_for_status()
    dest = os.path.join(output_dir, name)
    with open(dest, "wb") as f:
        f.write(r.content)
    return dest

program  = StudyProgram.objects.get(title_gr = PROGRAM_TITLE_GR)
dit  = Department.objects.get(title_gr = DEPARTMENT_TITLE_GR)

b = budiapi(master_url= URL,
            app_map = APP_MAP,
            table_ids = TABLES)

reports = b.get_table_data('reports', 'myphd')
for r in reports:
    url = MASTER_URL + r['pdf'][0]['url']
    name = r['pdf'][0]['name']
    email = r['candidateEmail']
    year = r['referenceYear']
    notes = r['comments']
    submission_date = r['Created At']
    dest = get_file(name, url)
    
    if Student.objects.filter(email=email).exists():
        student = Student.objects.get(email=email)
        thesis = PhdThesis.objects.get(candidate=student)
        report = ThesisProgress(
            thesis = thesis,
            year = year,
            submission_date = convert_date(submission_date),
            notes = notes
        )
        report.save()
        with open(dest, 'rb') as f:
            report.pdf.save(name, File(f), save=True)
        print(student, year)

    
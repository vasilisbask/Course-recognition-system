from budi import budiapi
import os
import sys
import django
import traceback
import requests
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myfaculty.settings")
django.setup()

from curricula.models import StudyProgram, Department
from myprofile.models import Student, StaffMember, PersonalInfo
from phdstuds.models import PhdThesis,Recommendation, ThesisProgress, JournalPublication, ConferencePublication, TeachingTask
from datetime import datetime, date
from django.core.files import File
from django.conf import settings
from django.utils import timezone

ALUMNI_CSV = 'alumni.csv'

correct_dicts = {
    'eliοtou@hua.gr' : 'eliotou@hua.gr'
}

def correct(s):
    if s in correct_dicts:
        return correct_dicts[s]
    else:
        return s

def convert_date(d):
    try:
        result = date.strptime(d, "%d/%m/%Y")
    except ValueError:
        result = datetime.fromisoformat(d).date()
    return result

def convert_rec(r):
    rec_budy = ['Οριακά Επαρκής', 'Μη Επαρκής - Διαγραφή', 'Ικανοποιητική']
    rec_django = [Recommendation.MARGINAL, Recommendation.UNSATISFACTORY, Recommendation.SATISFACTORY]
    i = rec_budy.index(r)
    return rec_django[i]

def clear_email(email):
    return email.strip().replace('\r', '').replace('\n', '').replace(' ','').replace(',','')

KEY = settings.BUDI_KEY
APP_ID = 'app_cb6ba908523b419caf31b44aa97e1c50'
TABLES = {
    'phds' : 'ta_0406b0e66c3d45bf823e14db055099bd',
    'faculty' : 'ta_ddf9e22686314f638721d931c85e1262',
    'reports' : 'ta_b696a4d0c73040299512d6894754cb9e',
    'recommendations' : 'ta_8c8a74ff3d44450bb1e25dd6b0a4864f',
    'journals' : 'ta_41b59bc53bca4530a3c3b168f7a10b28',
    'conferences' : 'ta_1df49a9c75714ff7bb2543079fabae92',
    'teaching' : 'ta_9a2b7e82e14847919723ed39015a0d72'
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

b = budiapi(api_key = KEY, 
            master_url= URL,
            app_map = APP_MAP,
            table_ids = TABLES)

budi_students = b.get_table_data('phds', 'myphd')
for element in budi_students:
    element['status'] = PhdThesis.ONGOING

with open(ALUMNI_CSV, 'r') as f:
    reader = csv.DictReader(f, delimiter=',')
    alumni_students = list(reader)

for element in alumni_students:
    for k,v in element.items():
        if 'mail' in k:
            v = v.replace('[dot]','.').replace('[at]','@').replace('[a]','@')
            element[k] = v
    element['status'] = PhdThesis.COMPLETED

students_to_import = budi_students + alumni_students    

print('Importing phd students...')
for student in students_to_import:
    surname = student['surname']
    given_name = student['givenName']
    email = clear_email(student['email'])
    reg_num = student['idNumber']
    username = email.split('@')[0]

    phd_student = Student(
            surname = surname,
            given_name = given_name,
            email = email,
            reg_num = reg_num,
            program = program,
            username = username
        )
    if not Student.objects.filter(email = email).exists():        
        phd_student.save()
    else:        
        phd_student = Student.objects.filter(email = email).first()
        phd_student.save()

    pi = phd_student.personal_info
    if 'Θ' in student['gender'] or 'θ' in student['gender']:
        pi.gender = PersonalInfo.GENDER_FEMALE
    elif 'Α' in student['gender'] or 'A' in student['gender']:
        pi.gender = PersonalInfo.GENDER_MALE
    pi.date_of_birth = convert_date(student['dateOfBirth'])
    pi.mobile_phone = student['mobilePhone']
    pi.fathers_name = student['fathersName']
    pi.secondary_email = student['externalEmail']
    pi.save()

# Make sure all students have user names
print('Creating users for students...')

for student in students_to_import:
    phd_student = Student.objects.get(email=clear_email(student['email']))
    phd_student.save()

print('Importing staff')
budi_staff = b.get_table_data('faculty', 'myphd')

for staff in budi_staff:
    email = clear_email(staff['email'])
    if '@' not in email:
        print('Encountered strange email address for %s' %email)
    elif not email.isascii():
        print('Non ascii characters in %s' %email)
    
    else:
        if not StaffMember.objects.filter(email = email).exists():
            given_name = staff['givenName']
            surname = staff['surname']
            title = staff.get('title','')
            institution = staff.get('insitution','')
            department = staff.get('department','')
            internal_department = dit
            is_internal = False
            staffmember = StaffMember(
                email = email,
                given_name = given_name,
                surname = surname,
                title = title,
                institution = institution,
                department = department,
                internal_department = internal_department,
                is_internal = is_internal
            )
            staffmember.save()

print('Setting supervisors and committees and assigning theses...')
for budi_student in students_to_import:
    
    student = Student.objects.get(email = clear_email(budi_student['email']))

    supervisor_email = correct(budi_student['supEmail'].strip())    
    if not StaffMember.objects.filter(email = supervisor_email).exists():
        print('supervisor with email %s does not exist.' %supervisor_email)
    else:
        supervisor = StaffMember.objects.get(email = supervisor_email)

    com = []

    com1_email = correct(budi_student['com1Email'].strip())
    if not StaffMember.objects.filter(email = com1_email).exists():
        print('Com1 with email %s does not exist.' %com1_email)
    else:
        com.append(
            StaffMember.objects.get(email = com1_email)
        )
    com2_email = correct(budi_student['com2Email'].strip())
    if not StaffMember.objects.filter(email = com2_email).exists():
        print('Com2 with email %s does not exist.' %com2_email)
    else:
        com.append(
            StaffMember.objects.get(email = com2_email)
        )

    if not PhdThesis.objects.filter(candidate=student).exists():
        thesis = PhdThesis()
    else:
        thesis = PhdThesis.objects.filter(candidate=student)

    inscription_year = budi_student['inscriptionYear']
    
    if '-' in inscription_year:
        inscription_year = int(inscription_year.split('-')[0])

    
    thesis.candidate = student
    thesis.supervisor = supervisor
    thesis.subject_gr = budi_student['subjectGr']
    thesis.subject_en = budi_student['subjectEn']
    thesis.inscription_year = inscription_year
    thesis.inscription_ga = budi_student['inscriptionRef']
    thesis.notes = budi_student['inscriptionNotes']
    thesis.status = budi_student['status']
    try:
        thesis.save()
        thesis.committee.set(com)
        thesis.save()
        
    except Exception:
        print('Problems in thesis %s' %thesis)            
        print(traceback.format_exc())    

print('Importing student reports...')    

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
        query = ThesisProgress.objects.filter(thesis=thesis, year=year)
        if query.exists():
            report = query.first()
        else:
            report = ThesisProgress()
        
        report.thesis = thesis
        report.year = year
        report.submission_date = convert_date(submission_date)
        report.notes = notes
        report.save()
        with open(dest, 'rb') as f:
            report.pdf.save(name, File(f), save=True)

recommendations = b.get_table_data('recommendations', 'myphd')
for rec in recommendations:
    email = rec['candidateEmail']
    year = rec['year']
    sup_email = rec['supEmail']
    recommendation = convert_rec(rec['recommendation'])
    submission_date = convert_date(rec['Created At'])
    recommender = StaffMember.objects.get(email = sup_email)
    try:
        thesis = PhdThesis.objects.get(candidate__email = email)
        if Recommendation.objects.filter(thesis=thesis, year=year).exists():
            r = Recommendation.objects.get(thesis=thesis, year=year)
        else:
            r = Recommendation()
        r.thesis = thesis
        r.year = year
        r.submission_date = submission_date
        r.recommendation = recommendation
        r.recommender = recommender
        r.save()
        if 'supportingDocument' in rec.keys():
            supporting_document = rec['supportingDocument']
            url = MASTER_URL + rec['supportingDocument'][0]['url']
            name = rec['supportingDocument'][0]['name']
            dest = get_file(name, url)    
            with open(dest, 'rb') as f:
                r.supporting_document.save(name, File(f), save=True)
                
    except Exception:
        print('Problems in recommendation %s %s' %(email, year))            
        print(traceback.format_exc()) 

budi_journals = b.get_table_data('journals', 'myphd')
budi_conferences = b.get_table_data('conferences', 'myphd')
budi_teaching = b.get_table_data('teaching', 'myphd')

for pub in budi_journals:
    pub_dict = {
        'email': pub['candidateEmail'],
        'title': pub['title'],
        'journal_title': pub['journal'],
        'volume': pub['volume'],
        'issue': pub['issue'],
        'year': pub['year'],
        'doi': pub['doi'],
        'author_list': pub['authorsList'],
        'has_supervisor': pub['hasSupervisor'],
        'publisher': pub['publisher'],
    }
    
    query = JournalPublication.objects.filter(title = pub_dict['title'])
    if not query.exists():
        django_pub = JournalPublication()
    else:
        django_pub = query.first()
    try:    
    
        thesis = PhdThesis.objects.get(candidate__email = clear_email(pub_dict['email']))

        for k, v in pub_dict.items():
            setattr(django_pub, k, v)

        django_pub.thesis = thesis
        django_pub.save()

    except Exception:
        print('Thesis not found for %s' %pub_dict)            
        print(traceback.format_exc())    

for pub in budi_conferences:
    pub_dict = {
        'email': pub['candidateEmail'],
        'title': pub['title'],
        'author_list': pub['authorsList'],
        'conference_title': pub['conferenceName'],        
        'year': pub['year'],
        'venue' : pub['venue'],        
    }
    query = ConferencePublication.objects.filter(title = pub_dict['title'])
    if not query.exists():
        django_pub = ConferencePublication()
    else:
        django_pub = query.first()
    
    for k, v in pub_dict.items():
        setattr(django_pub, k, v)

    try:
        thesis = PhdThesis.objects.get(candidate__email = clear_email(pub_dict['email']))
        django_pub.thesis = thesis

        django_pub.save()

    except Exception:
        print('Thesis not found for %s' %pub_dict)            
        print(traceback.format_exc())    

for task in budi_teaching:
    task_dict = {
        'email': task['candidateEmail'],
        'year': task['year'],
        'hours_per_week' : task['hoursPerWeek'],
        'no_weeks' : task['noWeeks'],
        'under_contract' : task['haveContract'],        
        'course_name' : task['courseName']
    }
    try:
        thesis = PhdThesis.objects.get(candidate__email = task['candidateEmail'])
        supervisor = StaffMember.objects.get(email = task['facultyEmail'])
        query = TeachingTask.objects.filter(course_name = task['courseName'], year = task['year'])

        if not query.exists():
            django_task = TeachingTask()
        else:
            django_task = query.first()
        
        for k, v in task_dict.items():
            setattr(django_task, k, v)
        django_task.thesis = thesis
        django_task.faculty = supervisor
        django_task.save()

    except Exception:
        print('Thesis not found for %s' %task_dict)                    
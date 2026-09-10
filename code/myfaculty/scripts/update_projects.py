from myprofile.models import StaffMember
from django.contrib.auth.models import User
from projects.models import Project
from django.core.files.temp import NamedTemporaryFile
from django.core import files
from scripts.budi import budiapi
import requests
from datetime import datetime

MASTER_URL = 'https://onestop.ditapps.hua.gr'

def get_file(sub_url, filename):
    memory_file = NamedTemporaryFile(delete=True)
    content = requests.get(MASTER_URL + sub_url)
    for block in content.iter_content(1024 * 8):
        if not block:
            break
        memory_file.write(block)
        memory_file.flush()

    temp_file = files.File(memory_file, name=filename)

    return temp_file   

def run():
    b = budiapi()
    projects = b.get_table_data('projects','projects')

    for p in projects:
        P = Project(
            is_editable = True,
            appoved = p['proposalApproved'] == 'true',
            submission_approved_ga = p['gaProposalApproved'],
            implementation_approved_ga = p['gaProjectApproved'],
            budget_total = float(p['proposalBudget']),
            budget_dep = float(p['departmentBudget']),
            call = p['call'],
            thematic_areas = p['thematicAreas'],
            title = p['title'],
            department_role = p['departmentRole'],
            department_staff = p['departmentStaff'],
            acronym = p['acronym'],
            abstract = p['abstract'],
            partners = p['partners'],
            funding_date = float(p['fundingRate']),
            duration = float(p['durationMonths']),
            start = datetime.fromisoformat(p['startDate']),
            coordinator = StaffMember.objects.get(email = p['coordinatorEmail']),
            created_date = datetime.fromisoformat(p['Created At']),
            updated_date = datetime.fromisoformat(p['Updated At'])
            
        )

        if p['gaSubmissionDoc']:
            ga_sub_file = p['gaSubmissionDoc'][0]['name']
            ga_sub_url = p['gaSubmissionDoc'][0]['url']
            P.document_approved_submission = get_file(ga_sub_url, ga_sub_file)

        if p['gaProjectDoc']:
            ga_project_file = p['gaProjectDoc'][0]['name']
            ga_project_url = p['gaProjectDoc'][0]['url']
            P.document_approved_implementation = get_file(ga_project_url, ga_project_file)
        
        P.save()
        print(P.title)        
from myprofile.models import StaffMember
from django.contrib.auth.models import User
from leaves.models import Leave
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
    leaves = b.get_table_data('leaves','leaves')

    for p in leaves:
        P = Leave(
            country = p['destinationCountry'],
            city = p['destinationCity'],
            organization = p['destinationOrganization'],
            start_date = datetime.fromisoformat(p['startDate']),
            end_date = datetime.fromisoformat(p['endDate']),
            applicant = StaffMember.objects.get(email = p['applicantEmail']),
            created_date = datetime.fromisoformat(p['Created At']),
            updated_date = datetime.fromisoformat(p['Updated At']),
            approved_ga = p.get('approvedGA',''),
            description = p['description'],
            project_title = p.get('projectTitle',''),
            project_code = p.get('projectCode',''),
        )

        if 'gaDocument' in p:
            if p['gaDocument']:
                print(p['gaDocument'])
                ga_sub_file = p['gaDocument'][0]['name']
                ga_sub_url = p['gaDocument'][0]['url']
                P.ga_document = get_file(ga_sub_url, ga_sub_file)
        
        try:
            P.travel_expenses = p['travelExpenses']
        except:
            P.travel_expenses = 0.0
        
        try:
            P.stay_expenses = p['stayExpenses']
        except:
            P.stay_expenses = 0.0
        
        try:
            P.registration_expenses = p['registrationExpenses']
        except:
            P.registration_expenses = 0.0
        
        P.save()
        print(P.city, P.country, P.applicant)        
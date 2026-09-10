from myprofile.models import StaffMember
from django.contrib.auth.models import User
from timesheets.models import Timesheet
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
    timesheets = b.get_table_data('timesheets','timesheets')

    for p in timesheets:
        try:    
            P = Timesheet(
                created_date = datetime.fromisoformat(p['Created At']),
                updated_date = datetime.fromisoformat(p['Updated At']),
                month = p['month'],
                year = p['year'],
                applicant = StaffMember.objects.get(email = p['email'])
            )

            if 'unsignedpdf' in p:
                if p['unsignedpdf']:
                    print(p['unsignedpdf'])
                    name = p['unsignedpdf'][0]['name']
                    url = p['unsignedpdf'][0]['url']
                    P.unsigned = get_file(url,name)
                    
            
            if 'signedpdf' in p:
                if p['signedpdf']:
                    print(p['signedpdf'])
                    name = p['signedpdf'][0]['name']
                    url = p['signedpdf'][0]['url']
                    P.signed = get_file(url,name)
            
            P.save()
            print(P)
        except Exception as e:
            print(e)        
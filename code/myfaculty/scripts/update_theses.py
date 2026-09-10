from myprofile.models import StaffMember
from django.contrib.auth.models import User
from theses.models import Thesis
from curricula.models import StudyProgram
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
    theses = b.get_table_data('theses','theses')

    undergraduate = StudyProgram.objects.get(title_gr='Προπτυχιακό Πρόγραμμα Σπουδών')
    it = StudyProgram.objects.get(title_gr='ΠΜΣ Πληροφορική και Τηλεματική')
    applied = StudyProgram.objects.get(title_gr='ΠΜΣ Εφαρμοσμένη Πληροφορική')
    mphil = StudyProgram.objects.get(title_gr='ΠΜΣ Επιστήμη των Υπολογιστών και Πληροφορική')

    for p in theses:
        print(p)
        try:  
            P = Thesis(
                created_date = datetime.fromisoformat(p['Created At']),
                updated_date = datetime.fromisoformat(p['Updated At']),
                title_gr = p['titleGr'],
                title_en = p['titleEn'],
                abstract = p['abstract'],
                supervisor = StaffMember.objects.get(email = p['supervisorEmail']),
                is_offered = p['isOffered'],                         
            )
        
            member1 = StaffMember.objects.filter(email = p['member1email'])
            member2 = StaffMember.objects.filter(email = p['member2email'])   

            if len(member1) > 0:
                P.member1 = member1[0]

            if len(member2) > 0:
                P.member2 = member2[0]
                
            P.save()

            if 'offeredUnder' in p:            
                if p['offeredUnder']:
                    P.offered_in.add(undergraduate)
            
            if 'offeredPost' in p:            
                if p['offeredPost']:
                    P.offered_in.add(it)
            
            if 'offeredApplied' in p:            
                if p['offeredApplied']:
                    P.offered_in.add(applied)
            
        except Exception as e:
            pass
        
from myprofile.models import StaffMember
from django.contrib.auth.models import User

import csv

MAP = {'surName': 'surname',
       'givenName':	'given_name',
       'email' : 'email',
       'title' : 'title',
       'internal' : 'is_interal',

       }

FILENAME = 'scripts/faculty.csv.tpl'
orig_keys = []

faculty_dicts =[]

def run():
    with open(FILENAME,'r') as f:
        reader = csv.reader(f, delimiter= ',')
        for i, row in enumerate(reader):
            if i==0:
                for k in row:
                    orig_keys.append(k)
            else:
                e = {}
                for j, v in enumerate(row):
                    k = orig_keys[j]
                    if k in MAP:
                        e[ MAP[k] ] = row[j]    
                print(e) 
                faculty_dicts.append(e)

    for e in faculty_dicts:
        exists = StaffMember.objects.filter(email=e['email']).count() > 0
        if exists:
            E = StaffMember.objects.get(email = e['email'])
            is_internal = e['is_interal'].title()
            E.is_internal = is_internal == 'True'
            E.save()
            print('Updated faculty with email ', e['email'])
            

            
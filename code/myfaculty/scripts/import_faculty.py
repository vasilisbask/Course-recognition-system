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
        if not exists:
            surname = e['surname'].title()
            given_name = e['given_name'].title()
            email = e['email'].lower()
            is_internal = e['is_interal'].title()
            title = e['title']
            E = StaffMember(surname = surname,
                            given_name = given_name,
                            email = email,
                            is_internal = is_internal == 'True',
                            title = title)
            E.save()
            print('Created associate with email ', e['email'])
            if '@' in email:
                username = email.split('@')[0]
                user_exists = User.objects.filter(username=username).count() > 0
                if not user_exists:
                    user = User(first_name = given_name,
                                last_name = surname,
                                email = email,
                                username = username)
                    user.save()
                    E.user = user
                    E.save()
                    print('Created user with username ', username)
            
        else:
            print(e['email'], 'already exists')
        

            
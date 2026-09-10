from myprofile.models import Associate, StaffMember
from django.contrib.auth.models import User

import csv
MAP = {'surname': 'surname',
       'givename':	'given_name',
       'associate_email' : 'email',
       'office' : 'office_no',
       'seat' : 'seat_no',
       'supervisor' : 'supervisor'
}

FILENAME = 'scripts/associates.csv.tpl'
orig_keys = []

associate_dicts =[]

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
                associate_dicts.append(e)

    for e in associate_dicts:
        exists = Associate.objects.filter(email=e['email']).count() > 0
        if not exists:
            surname = e['surname'].title()
            given_name = e['given_name'].title()
            email = e['email'].lower()
            supervisor = e['supervisor']
            office_no = e['office_no']
            seat_no = e['seat_no']
            
            E = Associate(surname = surname,
                         given_name = given_name,
                         email = email,
                         office_no = office_no,
                         seat_no = seat_no)
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
            print(supervisor)
            if '@' in supervisor:
                supervisor_exists = StaffMember.objects.filter(email=supervisor).count() > 0
                if supervisor_exists:
                    supervisor_obj = StaffMember.objects.get(email=supervisor)
                    E.supervisor = supervisor_obj
                    E.save()
                    print('Assigned associate with faculty ', supervisor_obj)
        else:
            print(e['email'], 'already exists')
        

            
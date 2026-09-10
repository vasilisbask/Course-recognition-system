import os

from django.conf import settings
from myprofile.models import StaffMember, Associate
from django.contrib.auth import get_user_model
from datetime import datetime

person = {

    'email' : 'staff@example.com',
    'given_name' : 'Demo',
    'surname' : 'Staff',
    'fathers_name' : 'Demo',
    'date_of_birth' : '01/01/1975',
    
    'tin' : '000000000',
    'ssn' : '000000000',

    'is_internal' : 'True',
    
    'institution' : 'Example University',
    'school' : 'Example School',
    'department' : 'Example Department',
    
    'title' : 'Professor',
    
    'home_address_street' : 'Example Street',
    'home_address_no' : '1',


    'home_address_po_box' : '00000',
    'home_address_city' : 'Example City',
    'home_address_country' : 'Example Country',
    'mobile_phone' : '0000000000',
    'home_phone' : '0000000000',

    'work_address_street' : '',
    'work_address_no' : '',
    'work_address_po_box' : '',
    'work_address_city' : '',
    'work_address_country' : '',
    'work_phone' : '',
}

associate = {

    'email' : 'associate@example.com',
    'given_name' : 'Demo',
    'surname' : 'Associate',
    'fathers_name' : 'Demo',
    'date_of_birth' : '01/01/1900',
    
    'tin' : '000000000',
    'ssn' : '000000000',

    'is_phd_student' : 'True',
    'is_postdoc' : 'False',
    
    
    'home_address_street' : 'Example Street',
    'home_address_no' : '1',
    'home_address_po_box' : '00000',
    'home_address_city' : 'Example City',
    'home_address_country' : 'Example Country',
    'mobile_phone' : '0000000000',
    'home_phone' : '0000000000',

    'work_phone' : '0000000000',
}

def translate_to_staff(s):
    d = {}
    for k, v in s.items():
        if v != '':            
            if k in ['home_address_no', 'home_address_po_box', 'work_address_no', 'work_address_po_box']:
                val = int(v)
            elif k in ['date_of_birth']:
                val = datetime.strptime(v, '%d/%m/%Y')
            else:
                val = v
            d[k] = val

    return StaffMember(**d)

def translate_to_associate(s):
    d = {}
    for k, v in s.items():
        if v != '' :            
            if k in ['home_address_no', 'home_address_po_box', 'work_address_no', 'work_address_po_box']:
                val = int(v)
            elif k in ['date_of_birth']:
                val = datetime.strptime(v, '%d/%m/%Y')
            else:
                val = v
            d[k] = val

    return Associate(**d)

def run():
    # Create superuser

    User = get_user_model()
    if not User.objects.filter(username = 'admin').exists():
        User.objects.create_superuser(
            'admin',
            os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
            os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'ChangeMe123!'),
        )

    if not StaffMember.objects.filter(email = person['email']).exists():
        E = translate_to_staff(person)
        # Check to see whether a user already exists

        username = E.email.split('@')[0]
        email = E.email
        u_query = User.objects.filter(username = username)
        if u_query.count() == 0:
            u = User(username = username, 
                    email = email)
            u.save()
        else:
            u = u_query[0]

        E.user = u
        E.save()

    if not Associate.objects.filter(email = person['email']).exists():
        A = translate_to_associate(associate)

        username = A.email.split('@')[0]
        email = A.email
        u_query = User.objects.filter(username = username)
        if u_query.count() == 0:
            u = User(username = username, 
                    email = email)
            u.save()
        else:
            u = u_query[0]

        A.user = u
        A.save()

        
      

    

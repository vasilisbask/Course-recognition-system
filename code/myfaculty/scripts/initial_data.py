from curricula.models import StudyProgram, School, Department, Institution
from myprofile.models import Student, StaffMember
from scopes.models import Secretariat
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

DEFAULT_DUMMY_PASS = 'test1234'

INSTITUTION = {
    'hua' : {
        'title_gr' : 'Χαροκόπειο Πανεπιστήμιο',
        'title_en' : 'Harokopio University', 
        'short_en' : 'hua',
        'class_type' : Institution,   
    }
}
SCHOOLS = {
    'dt' : {
        'title_gr' : 'Ψηφιακής Τεχνολογίας',
        'title_en' : 'Digital Technology',
        'short_en' : 'dt',
        'class_type' : School,
        'institution' : 'hua',   
    }
}
DEPARTMENTS = {
    'dit' : {
        'title_gr' : 'Πληροφορικής και Τηλεματικής',
        'title_en' : 'Informatics and Telematics',
        'school' : 'dt',
        'short_en' : 'dit',
        'class_type' : Department,   
    }
}
PROGRAMS = {
    'und' : {
        'title_gr' : 'Προπτυχιακό Πρόγραμμα Σπουδών',
        'title_en' : 'Undergraduate Program',
        'type' : StudyProgram.UNDERGRADUATE,
        'sis_code' : '550',
        'short_en' : 'und',
        'class_type' : StudyProgram,  
    }, 
    'csi' : {
        'title_gr' : 'Προηγμένες Τεχνολογίες Πληροφορικής και Εφαρμογές',
        'title_en' : 'Advances in Computer Science and Information Systems',
        'type' : StudyProgram.POSTGRADUATE,
        'sis_code' : '1550',
        'short_en' : 'csi',
        'class_type' : StudyProgram,  
    },
    'applied' : {
        'title_gr' : 'Εφαρμοσμένη Πληροφορικής',
        'title_en' : 'Applied Informatics',
        'type' : StudyProgram.DOCTORAL,
        'sis_code' : '1551',
        'short_en' : 'applied',
        'class_type' : StudyProgram,  
    }    
}

STAFF_MEMBERS = {
    'ng' : {
        'username' : 'ng',
        'email' : 'ng@hua.gr',
        'surname' : 'Νίκος',
        'given_name' : 'Γκάλης',
        'is_internal' : True,
        'title' : 'Καθηγητής',
        'internal_department' : 'dit',
        'class_type' : StaffMember,  
    }, 
    'pg' : {
        'username' : 'pg',        
        'email' : 'pg@hua.gr',        
        'surname' : 'Παναγιώτης',
        'given_name' : 'Γιαννάκης',
        'is_internal' : True,
        'title' : 'Καθηγητής',
        'internal_department' : 'dit',
        'class_type' : StaffMember,  
    },
    'mj' : {
        'username' : 'mj',
        'email' : 'mj@nba.com', 
        'surname' : 'Michael',
        'given_name' : 'Jordan',
        'is_internal' : True,
        'title' : 'Καθηγητής',
        'internal_department' : 'dit',
        'class_type' : StaffMember,  
    }
}
SECRETARIATS = {
    'und' : {
        'email' : 'undsec@hua.gr',
        'programs' : ['und'],
        'departments' : None,
        'class_type' : Secretariat,  
    },        
    'csi' : {
        'email' : 'csisec@hua.gr',
        'programs' : ['csi'],
        'departments' : None,
        'class_type' : Secretariat,  
    },
    'applied' : {
        'email' : 'appliedsec@hua.gr',
        'programs' : ['applied'],
        'departments' : None,
        'class_type' : Secretariat,  
    },
    'depsec' : {
        'email' : 'depsec@hua.gr',
        'programs' : None,
        'departments' : ['dit'],
        'class_type' : Secretariat,  
    }
}

def get_key(class_type):
    if class_type in [StaffMember]:
        return 'email'
    elif class_type in [Secretariat]:
        return 'program'    
    else:
        return 'short_en'
    
def queries(class_type, field_name, value):
    if value:
        if class_type == School:
            if field_name == 'institution':
                return Institution.objects.get(short_en = value)
        elif class_type == Department:
            if field_name == 'school':
                return School.objects.get(short_en = value)
        elif class_type == StudyProgram:
            if field_name == 'department':
                return Department.objects.get(short_en = value)            
        elif class_type == StaffMember:
            if field_name == 'internal_department':
               return Department.objects.get(short_en = value)
        elif class_type == Secretariat:
            if field_name == 'programs':
                return StudyProgram.objects.filter(short_en__in = value)
            if field_name == 'departments':
                return Department.objects.filter(short_en__in = value)
            
    
        
def get_or_create_user(email, password = DEFAULT_DUMMY_PASS):
    try:
        user = User.objects.get(email = email)
    except ObjectDoesNotExist:
        user = User()

    if '@hua.gr' in email:
        username = email.split('@')[0]
    else:
        username = email
    
    user.username = username
    user.set_password(password)
    user.email = email

    user.save()
    return user

def create_or_update_object(field_dict = {}):
    class_type = field_dict['class_type']
    key = get_key(class_type)
    print(field_dict)
    try:
        query = {key : field_dict[key]}
        object = class_type.objects.get( **query )
    except ObjectDoesNotExist:
        object = class_type()
    
    if 'email' in field_dict:
        email = field_dict['email']
        user = get_or_create_user(email)

    if hasattr(class_type, 'user'):
        object.user = user

    for k, v in field_dict.items():
        if hasattr(class_type,k):
            q = queries(class_type, k, v)
            if q:                
                setattr(object, k, q)
            else:
                setattr(object, k, v)

    object.save()

def run():

    DICTS = [INSTITUTION, SCHOOLS, DEPARTMENTS, PROGRAMS, STAFF_MEMBERS]

    for dict in DICTS:
        for key, object in dict.items():
            print(object)
            create_or_update_object(object)
    
    for key, sec in SECRETARIATS.items():
        print(sec)
        user = get_or_create_user(sec['email'])
        try:
            object = Secretariat.objects.get(user=user)
        except ObjectDoesNotExist:
            object = Secretariat(user=user)
        object.save()
        if sec['programs']:
            object.programs.set( StudyProgram.objects.filter(short_en__in = sec['programs']) )
        if sec['departments']:
            object.departments.set( Department.objects.filter(short_en__in = sec['departments']) )
        object.save()
        
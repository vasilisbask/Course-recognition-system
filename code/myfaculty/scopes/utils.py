
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, MultipleObjectsReturned
User = get_user_model()

def get_secreteriat_scope(user):
    from curricula.models import StudyProgram, Department
    from .models import Secretariat

    if isinstance(user, str):
        user = User.objects.get(username = user)

    if not user or not user.is_authenticated:
        return {
            'departments': Department.objects.none(),
            'programs': StudyProgram.objects.none(),
        }

    secretariats = Secretariat.objects.filter(user=user)
    if user.is_superuser:
        programs = StudyProgram.objects.all()
        departments = Department.objects.all()        

    elif secretariats.count() == 1:
        departments = secretariats.first().departments.all()
        sec_programs = secretariats.first().programs
        programs = StudyProgram.objects.filter(Q(id__in = sec_programs.values_list('id'))
                                               | Q(department__in = departments))    
    else:
        programs = StudyProgram.objects.none()
        departments = Department.objects.none()

    return {'departments' : departments, 'programs' : programs}

def get_scoped_object_or_exc(class_type, *args, user = None, **kwargs):

    scoped_objects = class_type.objects.filter(*args, **kwargs)
    if scoped_objects.count() == 0:
        raise ObjectDoesNotExist
    elif scoped_objects.count() > 1:
        raise MultipleObjectsReturned
    
    obj = scoped_objects.first()
    if obj.is_in_scope_of(user):
        return obj
    else:
        raise PermissionDenied
    



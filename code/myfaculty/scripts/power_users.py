from django.conf import settings
from myprofile.models import StaffMember, Associate
from django.contrib.auth import get_user_model
from datetime import datetime
from django.contrib.auth.models import Permission
User = get_user_model()
users=['daneli','itsec','apresvelou','thkam']

def run():
    ps = Permission.objects.get(codename='is_secreteriat')
                            
    for username in users:
        u = User.objects.filter(username=username)

        if len(u) > 0:
            print(username, 'already exists')
            user = User.objects.get(username=username)
        else:
            user = User(username=username)
            user.save()
        if ps not in user.user_permissions.all():
            user.user_permissions.add(ps)


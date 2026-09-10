from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend, ModelBackend
from django.conf import settings

UserModel = get_user_model()
internal_email = '@' + settings.INTERNAL_DOMAIN

class CustomAuthBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None):

        ldap_backend = LDAPBackend()
        db_backend = ModelBackend()

        # Username must be supplied
        if not username:
            return None
        
        # Check for internal email: if user logs in with internal email then use LDAP backend
        if internal_email in username:
            bare_username = username.split('@')[0]
            ldap_user = ldap_backend.authenticate(request, username=bare_username, password=password)
            if ldap_user:
                return ldap_user


        # Do we attempt login using username? If so check both ldap and then Django backend
        if '@' not in username:
            ldap_user = ldap_backend.authenticate(request, username=username, password=password)
            if ldap_user:
                return ldap_user    
            else:
                return db_backend.authenticate(request, username=username, password=password)
            
        # Finally check if you can login a user with his email in the Django backend
        if '@' in username:
            users = UserModel.objects.filter(email=username)
            if users.count()==1:
               return db_backend.authenticate(request, username=users[0].username, password=password)
            
    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


            
        





from django.db import models
from django.contrib.auth import get_user_model
from scopes.utils import get_secreteriat_scope
from django.core.exceptions import PermissionDenied

User = get_user_model()
# Create your models here.

class Secretariat(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    programs = models.ManyToManyField('curricula.StudyProgram', blank=True)
    departments = models.ManyToManyField('curricula.Department', blank=True)

    def __str__(self):
        if self.user:
            return 'Secretariat user %s' % self.user.username
        else:
            return 'Secretariat user'
        
    def program_scope(self):
        return self.programs.all()
    
    def department_scope(self):
        return self.departments.all()

class ScopedQueryPrg(models.QuerySet):
    def scope_filter(self, scope):
        return self.filter(program__in=scope['programs'])
    
    def in_scope_of(self, user):
        scope = get_secreteriat_scope(user)
        return self.scope_filter(scope)

    def sc_get(self, *args, user=None, **kwargs): 
        if not user:
            raise ValueError("You must pass user= to ScopedManagerPrg.sc_get()")
                   
        return self.in_scope_of(user).get(*args, **kwargs)   

    def sc_filter(self, *args, user=None, **kwargs):
        if not user:
            raise ValueError("You must pass user= to ScopedManagerPrg.sc_filter()")
          
        return self.in_scope_of(user).filter(*args, **kwargs)
              
class ScopedModelPrg(models.Model):

    class Meta:
        abstract = True

    objects = ScopedQueryPrg.as_manager()
    
    def scope_query(self, scope):
        return scope['programs'].filter(id = self.program.id).exists()
        
    def is_in_scope_of(self, user):
        scope = get_secreteriat_scope(user)        
        return self.scope_query(scope)
        
    def in_scope_or_403(self, user):
        if not self.is_in_scope_of(user):
            raise PermissionDenied()
        
class ScopedQueryDep(ScopedQueryPrg):

    def scope_filter(self, scope):
        return self.filter(department__in = scope['departments'])
    

class ScopedModelDep(ScopedModelPrg):
    
    class Meta:
        abstract = True

    objects = ScopedQueryDep.as_manager()    
    def scope_query(self, scope):
        return scope['departments'].filter(id = self.program.id).exists()
        
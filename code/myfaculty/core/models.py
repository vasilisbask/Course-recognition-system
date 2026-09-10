from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from scopes.models import ScopedModelDep, ScopedModelPrg
from core.utils import get_lang
from romanize import romanize

User = get_user_model()
# Create your models here.

class TitleStrMixin:

    def __str__(self):
        lang = get_lang()
        if lang == 'en':
            if hasattr(self, 'title_en'):
                if self.title_en and (self.title_en != ''):
                    return self.title_en
        return self.title_gr

class PersonStrMixin:

    def __str__(self):
        lang = get_lang()
        if lang == 'en':
            if hasattr(self, 'surname_en') and hasattr(self, 'given_name_en'):
                if self.surname_en and (self.surname_en != '') and self.given_name_en and (self.given_name_en != ''):
                    return self.given_name_en + ' ' +self.surname_en
            return romanize(self.given_name) + ' ' + romanize(self.surname)
            
        return self.given_name + ' ' +self.surname


class TrackedModel(models.Model):

    class Meta:
        abstract = True
    
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(app_label)s_%(class)s_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(app_label)s_%(class)s_updated")

    def save(self, *args, update_user = None, **kwargs):
        
        if isinstance(update_user, str):
            update_user = User.objects.get(username = update_user)

        now = timezone.now()

        self.updated_at = now
        self.updated_by = update_user

        if not self.id:
            self.created_at = now
            self.created_by = update_user

        super().save(*args, **kwargs)

class TrackedScopedProgramModel(ScopedModelPrg, TrackedModel):

    class Meta:
        abstract = True

class TrackedScopedDepartmentModel(ScopedModelDep, TrackedModel):
    class Meta:
        abstract = True
   
def get_or_create_object(model_class, update_user = None, **kwargs):
    objects = model_class.objects.filter(**kwargs)
    if objects.exists():
        object = objects.first()
    else:
        object = model_class(**kwargs)
        object.save(update_user = update_user)
    return object

def get_latest_or_create(model_class, update_user = None, **kwargs):
    objects = model_class.objects.filter(**kwargs).order_by('-updated_at')
    if objects.exists():
        object = objects.first()
    else:
        object = model_class(**kwargs)
        object.save(update_user = update_user)
    return object
from django.contrib import admin
from .models import Call, Application, Applicant, Degree, ReferenceLetter, JournalPublication, ConferencePublication, ReferenceContact, AppPersonalInfo
# Register your models here.

# Register your models here.
admin.site.register(Call)
admin.site.register(Application)
admin.site.register(AppPersonalInfo)
admin.site.register(Applicant)
admin.site.register(Degree)
admin.site.register(ReferenceLetter)
admin.site.register(JournalPublication)
admin.site.register(ConferencePublication)
admin.site.register(ReferenceContact)

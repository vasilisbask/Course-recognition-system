from django.contrib import admin
from .models import PhdThesis, JournalPublication, ConferencePublication, TeachingTask, ExamSupervision, AdministrativeTask, ThesisProgress, Recommendation
# Register your models here.

admin.site.register(PhdThesis)
admin.site.register(JournalPublication)
admin.site.register(ConferencePublication)
admin.site.register(TeachingTask)
admin.site.register(ExamSupervision)
admin.site.register(AdministrativeTask)
admin.site.register(ThesisProgress)
admin.site.register(Recommendation)
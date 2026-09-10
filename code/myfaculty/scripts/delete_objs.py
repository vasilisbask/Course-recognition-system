from phdapplications.models import *
from django.contrib.auth import get_user_model

models = [Call, Application, Applicant, AppPersonalInfo, Degree, WorkExperience, JournalPublication, ConferencePublication, ReferenceLetter, ReferenceContact]
def run():
    for class_name in models:
        for l in class_name.objects.all():
            l.delete()

users = ['demo@example.com']

User = get_user_model()

for username in users:
    users = User.objects.filter(username = username)
    if users.exists():
        for user in users:
            user.delete()

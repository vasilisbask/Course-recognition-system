from budi import budiapi
import os
import sys
import django
import traceback
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myfaculty.settings")
django.setup()

from curricula.models import StudyProgram, Department
from myprofile.models import Student, StaffMember, PersonalInfo
from phdstuds.models import PhdThesis,Recommendation, ThesisProgress, JournalPublication, ConferencePublication, TeachingTask
from datetime import datetime
from django.core.files import File

models_to_delete = [PhdThesis, Recommendation, ThesisProgress, JournalPublication, ConferencePublication, TeachingTask]
#models_to_delete = [TeachingTask]
for model in models_to_delete:
    for object in model.objects.all():
        object.delete()
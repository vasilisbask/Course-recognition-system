from budi import budiapi
import os
import sys
import django
import traceback
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myfaculty.settings")
django.setup()

from myprofile.models import Student, StaffMember, Associate

for model in [Student, StaffMember, Associate]:
    objs = model.objects.all()
    for obj in objs:
        obj.save()
        print(obj)
from django.db import models
from myprofile.models import Student, StaffMember
from curricula.models import Course
from datetime import datetime
# Create your models here.

class Attendance:
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField()
    ref_date = models.DateTimeField()
    student = models.ForeignKey(Student, on_delete=models.SET_NULL)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL)
    staffmember = models.ForeignKey(StaffMember, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        
        if not self.id and not self.created_date:
            self.created_date = datetime.now()

        if self.id and not self.updated_date:
            self.updated_date = datetime.now()

        super().save(*args, **kwargs)


    





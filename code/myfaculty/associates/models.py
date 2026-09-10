from django.db import models
from myprofile.models import Associate
from datetime import datetime

# Create your models here.


class Attendance(models.Model):
    CHECK_IN = 'in'
    CHECK_OUT = 'out'

    CHECK_CHOICES = {
        CHECK_IN : 'Είσοδος',
        CHECK_OUT : 'Έξοδος',
    }
    associate = models.ForeignKey(Associate, on_delete = models.SET_NULL, null = True)
    card_no = models.CharField(max_length = 40)
    date_time = models.DateTimeField()
    check_type = models.CharField(max_length=40, choices = CHECK_CHOICES)

    def __str__(self):
        return self.associate.surname + ' ' + self.associate.given_name + ' (' + self.check_type + ') ' + self.date_time.strftime('%Y-%m-%d: %H:%M')
    
class Card(models.Model):
    card_no = models.CharField(max_length = 40)
    updated_time = models.DateTimeField()
    
    def __str__(self):
        return 'Card with %s' %self.card_no

    def save(self, *args, **kwargs):
        self.updated_time = datetime.now()
        super().save(*args, **kwargs)


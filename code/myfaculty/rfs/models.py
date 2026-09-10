from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class ReferenceEntry(models.Model):

    DOCTORATE_APPLICATION = 'PHDAPP-DOC'
    REFERENCE_LETTER = 'PHDAPP-LET'
    DOC_THESIS_REPORT = 'DOCT-REP'

    CATEGORY_CHOICES = (
        (DOCTORATE_APPLICATION, _('Αίτηση για Διδακτορική Διατριβή')),
        (REFERENCE_LETTER, _('Συστατική Επιστολή')),
        (DOC_THESIS_REPORT, _('Αναφορά Προόδου Διδακτορικής Διατριβής')),
    )

    date_created = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    number = models.BigIntegerField(null=True, blank=True)
    category = models.CharField(null=True, blank=True, choices=CATEGORY_CHOICES)

    def save(self, *args, **kwargs):

        if not self.id:
            self.date_created = timezone.now()
        
            if not ReferenceEntry.objects.exists():
                self.number = 1
            else:
                self.number = ReferenceEntry.objects.order_by('-number').first().number + 1
        super().save(*args, **kwargs)

    def display_name(self):
        if self.category:
            return '%s-%s : %s' %(self.category, self.number, self.date_created.strftime("%Y-%m-%d"))
        else:
            return '%s : %s' %(self.number, self.date_created.strftime("%Y-%m-%d"))

    def __str__(self):
        if self.category:
            return '%s-%s : %s' %(self.category, self.number, self.date_created.strftime("%Y-%m-%d"))
        else:
            return '%s : %s' %(self.number, self.date_created.strftime("%Y-%m-%d"))





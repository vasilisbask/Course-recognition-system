from theses.models import Thesis
from django.forms.models import model_to_dict
import csv


def run():
    theses_assigned = Thesis.objects.filter(assigned_to__isnull=False)
    for thesis in theses_assigned:
        print(thesis)

        if not thesis.official_date:
            if not thesis.assignment_date:
                print(thesis.id, 'has no assignment date, using update_date')
                thesis.official_date = thesis.updated_date
            else:
                print(thesis.id, 'has assignment date, using that')
                thesis.official_date = thesis.assignment_date
        
        if not thesis.declared:
            thesis.declared = True
            thesis.declared_date = thesis.official_date
        thesis.save()

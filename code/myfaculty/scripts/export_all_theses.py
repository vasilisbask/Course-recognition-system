from theses.models import Thesis
from django.forms.models import model_to_dict
import csv


def run():
    theses_assigned = Thesis.objects.filter(assigned_to__isnull=True)
    theses_to_export =[]
    for thesis in theses_assigned:
        thesis_dict = model_to_dict(thesis)
        theses_to_export.append(thesis_dict)

    keys = theses_to_export[0].keys()

    with open('theses_assigned.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(theses_to_export)

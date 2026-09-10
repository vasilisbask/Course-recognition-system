from myprofile.models import StaffMember

def run():
    for staff in StaffMember.objects.all():
        staff.save()
        print(staff.display_name_en)

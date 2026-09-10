from curricula.models import Department
from myprofile.models import StaffMember, Associate

DEP_TITLE = 'Πληροφορικής και Τηλεματικής'
KEY = 'Τηλεματ'

def run():
    department = Department.objects.get(title_gr = DEP_TITLE)
    staff_members = StaffMember.objects.all()
    for staff_member in staff_members:
        staff_member.internal_department = None
        if KEY in staff_member.department:
            staff_member.internal_department = department
        staff_member.save()
        print(staff_member)

    associates = Associate.objects.all()

    for associate in associates:
        associate.save()



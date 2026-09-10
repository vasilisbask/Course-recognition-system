from django.contrib import admin
from .models import StaffMember, Associate, CustomUserPermissions, Student, PersonalInfo
# Register your models here.
admin.site.register(StaffMember)
admin.site.register(Associate)
admin.site.register(CustomUserPermissions)
admin.site.register(Student)

admin.site.register(PersonalInfo)


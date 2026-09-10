from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from myprofile.checks import likely_student_username
from .models import Student

# @receiver(user_logged_in)
# def check_student(sender, user, **kwargs):
#     username = user.username
#     print(username)
#     if likely_student_username(user):
#         Student.objects.get_profile(username)
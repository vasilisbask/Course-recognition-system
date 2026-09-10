from rest_framework import serializers
from django.contrib.auth.models import User
from myprofile.models import StaffMember, Associate
from associates.models import Attendance
from curricula.models import Course

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffMember
        fields = ["email", "surname"]

class AssociateSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Associate
        fields = ['surname', 'given_name', 'email']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['program',
                 'code_gr', 
                 'code_en', 
                 'semester',
                'title_gr',
                'title_en' ,    
                'weekly_hours', 
                'weekly_lab_hours',
                'ects_credits' ,
                'type_gr', 
                'type_en' ,
                'prequesites_gr',
                'prequesites_en' ,   
                'url',
                'language_gr', 
                'language_en', 
                'offered_erasmus',
                'outcomes_gr',
                'outcomes_en',
                'skills_gr' ,
                'skills_en' ,
                'content_gr' ,
                'content_en' ,
                'delivery_gr' ,
                'delivery_en' ,
                'ict_gr' ,
                'ict_en' ,
                'elective', 
                'hours_lecturing', 
                'hours_lab', 
                'hours_study', 
                'hours_project', 
                'hours_lab_prep',
                 ]
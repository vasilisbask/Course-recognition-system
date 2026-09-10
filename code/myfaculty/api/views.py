from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from myprofile.models import StaffMember, Associate
from associates.models import Attendance, Card
from curricula.models import Course

from .serializers import StaffSerializer, AssociateSeralizer, CourseSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from datetime import datetime

# Create your views here.

class StaffMemberApiView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        staff = StaffMember.objects.filter(email = email)
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AssociateApiView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        card_no = request.GET.get('card_no')
        associate = Associate.objects.filter(card_no = card_no)
        serializer = AssociateSeralizer(associate, many = True)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)

class CourseApiView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        id = request.GET.get('id')
        course = Course.objects.filter(pk = id)
        serializer = CourseSerializer(course, many=True)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)


class AttendanceApiView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        card_no = request.data.get('card_no')
        now = datetime.now()
        now_date = now.date()
    
        associates = Associate.objects.filter(card_no = card_no)
        
        if associates.count() > 0:
            associate = associates[0]
            existing_attendances = Attendance.objects.filter(date_time__contains = now_date, associate = associate)
            
            if existing_attendances.count() % 2 == 1:
                check_type = Attendance.CHECK_OUT
            else:
                check_type = Attendance.CHECK_IN
            
            attendance = Attendance(
                card_no = card_no,
                date_time = now,
                check_type = check_type,
                associate = associate
            )
            attendance.save()

            serializer = AssociateSeralizer(associates, many = True)
            data = serializer.data
            data[0]['count'] = existing_attendances.count()
            data[0]['check_type'] = check_type
                    

            return Response(data, status=status.HTTP_200_OK)
        
        else:
            serializer = AssociateSeralizer([], many = True)
            card = Card(card_no = card_no)
            card.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


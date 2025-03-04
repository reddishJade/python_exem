from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import User, Student, PhysicalStandard, TestPlan, TestResult, Comment, HealthReport
from .serializers import (
    UserSerializer, StudentSerializer, PhysicalStandardSerializer,
    TestPlanSerializer, TestResultSerializer, CommentSerializer, HealthReportSerializer
)

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            return Response({
                'token': 'token_will_be_implemented',
                'user_type': user.user_type,
                'username': user.username
            })
        return Response({'error': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return Student.objects.all()
        elif self.request.user.user_type == 'student':
            return Student.objects.filter(user=self.request.user)
        return Student.objects.none()

class PhysicalStandardViewSet(viewsets.ModelViewSet):
    queryset = PhysicalStandard.objects.all()
    serializer_class = PhysicalStandardSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

class TestPlanViewSet(viewsets.ModelViewSet):
    queryset = TestPlan.objects.all()
    serializer_class = TestPlanSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return TestResult.objects.all()
        elif self.request.user.user_type == 'student':
            return TestResult.objects.filter(student__user=self.request.user)
        return TestResult.objects.none()
    
    @action(detail=False, methods=['get'])
    def makeup_list(self, request):
        queryset = self.get_queryset().filter(total_score__lt=60, is_makeup=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student_profile)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        if request.user.user_type != 'admin':
            return Response({'error': '没有权限'}, status=status.HTTP_403_FORBIDDEN)
        comment = self.get_object()
        comment.is_approved = True
        comment.save()
        return Response({'status': '评论已审核通过'})

class HealthReportViewSet(viewsets.ModelViewSet):
    queryset = HealthReport.objects.all()
    serializer_class = HealthReportSerializer
    
    def get_queryset(self):
        if self.request.user.user_type == 'admin':
            return HealthReport.objects.all()
        elif self.request.user.user_type in ['student', 'parent']:
            return HealthReport.objects.filter(test_result__student__user=self.request.user)
        return HealthReport.objects.none()

from django.shortcuts import render

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User

from . import models
from .models import Task, TaskPermission
from .serializers import TaskSerializer, TaskPermissionSerializer, CreateTaskPermissionSerializer, UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            models.Q(owner=user) |
            models.Q(permissions__user=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        task = self.get_object()
        if task.owner != request.user:
            return Response({'detail': 'Только владелец может просматривать права доступа.'},
                            status=status.HTTP_403_FORBIDDEN)
        permissions = task.permissions.all()
        serializer = TaskPermissionSerializer(permissions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def grant_permission(self, request, pk=None):
        task = self.get_object()
        if task.owner != request.user:
            return Response({'detail': 'Только владелец может выдавать права доступа.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = CreateTaskPermissionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, granted_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def revoke_permission(self, request, pk=None):
        task = self.get_object()
        if task.owner != request.user:
            return Response({'detail': 'Только владелец может отзывать права доступа.'},
                            status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        permission = request.data.get('permission')

        if not user_id or not permission:
            return Response({'detail': 'Необходимо указать user_id и permission.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            permission_obj = task.permissions.get(user_id=user_id, permission=permission)
            permission_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TaskPermission.DoesNotExist:
            return Response({'detail': 'Указанное право доступа не найдено.'},
                            status=status.HTTP_404_NOT_FOUND)


class TaskPermissionViewSet(viewsets.ModelViewSet):
    serializer_class = TaskPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TaskPermission.objects.filter(granted_by=self.request.user)

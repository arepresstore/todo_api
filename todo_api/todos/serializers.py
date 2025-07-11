from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, TaskPermission

# Сериализатор для пользователя
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Сериализатор для задач
class TaskSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'created_at', 'updated_at', 'owner']
        read_only_fields = ['created_at', 'updated_at', 'owner']

# Сериализатор для прав доступа
class TaskPermissionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    granted_by = UserSerializer(read_only=True)

    class Meta:
        model = TaskPermission
        fields = ['id', 'task', 'user', 'permission', 'granted_by']
        read_only_fields = ['granted_by']

    def validate(self, data):
        # Проверяем, что текущий пользователь - владелец задачи
        if self.context['request'].user != data['task'].owner:
            raise serializers.ValidationError("Только владелец задачи может управлять правами доступа.")
        return data

# Сериализатор для создания прав доступа
class CreateTaskPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskPermission
        fields = ['task', 'user', 'permission']

    def validate(self, data):
        # Проверяем, что текущий пользователь - владелец задачи
        if self.context['request'].user != data['task'].owner:
            raise serializers.ValidationError("Только владелец задачи может управлять правами доступа.")
        return data
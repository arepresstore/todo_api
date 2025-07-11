from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

# Модель для хранения задач
class Task(models.Model):
    # Типы прав доступа
    class PermissionType(models.TextChoices):
        READ = 'READ', 'Чтение'
        UPDATE = 'UPDATE', 'Обновление'

    title = models.CharField(max_length=200, validators=[MinLengthValidator(1)])
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')

    def __str__(self):
        return self.title

# Модель для хранения прав доступа к задачам
class TaskPermission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_permissions')
    permission = models.CharField(max_length=10, choices=Task.PermissionType.choices)
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions')

    class Meta:
        unique_together = ('task', 'user', 'permission')  # Уникальная комбинация

    def __str__(self):
        return f"{self.user.username} can {self.permission} task {self.task.id}"

# Create your models here.

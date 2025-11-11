from django.db import models
from django_softdelete.models import SoftDeleteModel
from django.contrib.auth.models import User

class Profile(SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    security_question = models.CharField(max_length=255, null=True, blank=True)
    security_answer = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
    
class Task(SoftDeleteModel):
    class Priority(models.TextChoices):
        HIGH = 'High', 'High'
        MID = 'Mid', 'Mid'
        LOW = 'Low', 'Low'

    class Status(models.TextChoices):
        NOT_STARTED = 'Not Started', 'Not Started'
        IN_PROGRESS = 'In Progress', 'In Progress'
        COMPLETED = 'Completed', 'Completed'

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    assignees = models.ManyToManyField(Profile, related_name='tasks', blank=True)
    description = models.TextField(null=True, blank=True)
    due_datetime = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MID
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.NOT_STARTED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.priority}) - {self.status}"

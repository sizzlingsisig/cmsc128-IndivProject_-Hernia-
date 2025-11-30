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

class CollaborativeList(SoftDeleteModel):
    """Represents a shared todo list"""
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='owned_lists')
    members = models.ManyToManyField(Profile, related_name='collaborative_lists', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} (Owner: {self.owner.user.username})"

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
    created_by = models.ForeignKey(
    Profile,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='created_tasks'
    )
    title = models.CharField(max_length=200)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
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
    collaborative_list = models.ForeignKey(
        CollaborativeList, 
        on_delete=models.CASCADE, 
        related_name='tasks', 
        null=True, 
        blank=True
    )
    def __str__(self):
        return f"{self.title} ({self.priority}) - {self.status}"

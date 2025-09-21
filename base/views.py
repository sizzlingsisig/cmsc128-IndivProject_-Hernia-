from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from django.utils import timezone
from .serializers import TaskSerializer
from rest_framework import generics


# Home page: list tasks by priority
def home(request):
    lowPriorityTasks = Task.objects.filter(priority=Task.Priority.LOW)
    midPriorityTasks = Task.objects.filter(priority=Task.Priority.MID)
    highPriorityTasks = Task.objects.filter(priority=Task.Priority.HIGH)

    context = {
        'lowPriorityTasks': lowPriorityTasks,
        'midPriorityTasks': midPriorityTasks,
        'highPriorityTasks': highPriorityTasks,
    }
    return render(request, 'base/home.html', context)


class TaskListCreate(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


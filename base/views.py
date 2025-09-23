from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Task
from .serializers import TaskSerializer
from django.shortcuts import render

def home(request):
    tasks = Task.objects.all()
    context = {
        'tasks': tasks
    }
    return render(request, 'base/home.html', context)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        include_deleted = self.request.query_params.get('deleted', 'false').lower() == 'true'
        if include_deleted:
            return Task.global_objects.all() 
        return Task.objects.all() 

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        task.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        task = get_object_or_404(Task.global_objects, pk=pk)  
        task.restore()
        serializer = self.get_serializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

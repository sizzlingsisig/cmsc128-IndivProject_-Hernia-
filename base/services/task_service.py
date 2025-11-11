from django.shortcuts import get_object_or_404
from ..models import Task

class TaskService:

    @staticmethod
    def delete_task(task):
        task.delete()

    @staticmethod
    def restore_task(pk):
        task = get_object_or_404(Task.global_objects, pk=pk)
        task.restore()
        return task

    @staticmethod
    def add_assignee(task, profile):
        task.assignees.add(profile)

    @staticmethod
    def remove_assignee(task, profile):
        task.assignees.remove(profile)

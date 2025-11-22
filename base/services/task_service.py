from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.exceptions import ValidationError, PermissionDenied

from ..models import Task, CollaborativeList


class TaskService:

    @staticmethod
    def get_collaborative_tasks(profile, list_id=None):
        """Get collaborative tasks accessible to a user"""
        accessible_lists = CollaborativeList.objects.filter(
            Q(owner=profile) | Q(members=profile)
        ).distinct()
        
        if list_id:
            return Task.objects.filter(
                collaborative_list_id=list_id,
                collaborative_list__in=accessible_lists
            )
        
        return Task.objects.filter(collaborative_list__in=accessible_lists)

    @staticmethod
    def get_personal_tasks(profile):
        """Get personal tasks for a user"""
        return Task.objects.filter(
            profile=profile,
            collaborative_list__isnull=True
        )

    @staticmethod
    def create_in_collaborative_list(collab_list_id, user_profile, task_data):
        """
        Create task in collaborative list
        
        Raises:
            ValidationError: If list not found
            PermissionDenied: If user doesn't have access
        """
        try:
            collab_list = CollaborativeList.objects.get(id=collab_list_id)
            
            # Check access
            if collab_list.owner != user_profile and user_profile not in collab_list.members.all():
                raise PermissionDenied("No access to this list")
            
            return {
                'collaborative_list': collab_list,
                'created_by': user_profile
            }
            
        except CollaborativeList.DoesNotExist:
            raise ValidationError("Collaborative list not found")

    @staticmethod
    def create_personal_task(user_profile):
        """Get data for creating a personal task"""
        return {
            'profile': user_profile,
            'created_by': user_profile
        }

    @staticmethod
    def check_task_ownership(task, user_profile):
        """
        Check if user can modify a task
        
        For collaborative tasks: user must be the creator (created_by)
        For personal tasks: user must be the profile owner
        
        Raises:
            PermissionDenied: If user doesn't have permission to modify
        """
        # Checks if it's a collaborative task
        if task.collaborative_list:
            if task.created_by != user_profile:
                raise PermissionDenied("You cannot modify this task")
        else:
            if task.profile != user_profile:
                raise PermissionDenied("You cannot modify this task")

    @staticmethod
    def delete_task(task):
        """Soft delete a task"""
        task.delete()

    @staticmethod
    def restore_task(pk):
        """Restore a soft-deleted task by primary key"""
        task = get_object_or_404(Task.global_objects, pk=pk)
        task.restore()
        return task

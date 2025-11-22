# Standard library
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

# Third-party
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import api_view, action, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

# Local
from .models import Task, CollaborativeList
from .serializers import (
    UserSerializer,
    TaskSerializer,
    SetSecurityQuestionSerializer,
    CollaborativeListSerializer
)
from .services.user_service import UserService
from .services.task_service import TaskService
from .services.collaborative_list_service import CollaborativeListService


""" Home, Tasks, and Profile Views
These render the main HTML pages for the application."""

def tasks(request):
    return render(request, "base/tasks.html")


def auth(request):
    return render(request, "base/auth.html")


def profile(request):
    return render(request, "base/profile.html")

def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'base/404.html', status=404)

# Collaborative List Controller 
class CollaborativeListViewSet(viewsets.ModelViewSet):
    serializer_class = CollaborativeListSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    # Get lists accessible to the user
    def get_queryset(self):
        if not hasattr(self.request.user, "profile"):
            return CollaborativeList.objects.none()
        
        return CollaborativeListService.get_accessible_lists(self.request.user.profile)
    
    # Create new collaborative list with owner as the requesting user
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)
    
    # Add member to collaborative list
    @action(detail=True, methods=['post'])  
    def add_member(self, request, pk=None):
        collab_list = self.get_object()
        username = request.data.get('username')
        
        try:
            CollaborativeListService.add_member(
                collab_list=collab_list,
                username=username,
                requester_profile=request.user.profile
            )
            return Response({"success": f"Added {username} to list"})
            
        except PermissionDenied as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ObjectDoesNotExist as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

# Task Controller
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    # Get tasks based on view type and list id
    def get_queryset(self):
        """Used for list operations"""
        if not hasattr(self.request.user, "profile"):
            return Task.objects.none()
        
        view_type = self.request.query_params.get('view', 'personal')
        list_id = self.request.query_params.get('list_id')
        
        if view_type == 'collaborative':
            return TaskService.get_collaborative_tasks(self.request.user.profile, list_id)
        
        return TaskService.get_personal_tasks(self.request.user.profile)

    def get_object(self):
        """
        Override get_object to allow access to both personal and collaborative tasks
        for detail operations (retrieve, update, delete)
        """
        task_id = self.kwargs.get('pk')
        profile = self.request.user.profile
        
        # Get all tasks user has access to (personal + collaborative)
        personal_tasks = TaskService.get_personal_tasks(profile)
        collaborative_tasks = TaskService.get_collaborative_tasks(profile)
        
        # Combine both querysets
        from django.db.models import Q
        accessible_tasks = Task.objects.filter(
            Q(id__in=personal_tasks) | Q(id__in=collaborative_tasks)
        )
        
        try:
            task = accessible_tasks.get(pk=task_id)
            # Check object permissions
            self.check_object_permissions(self.request, task)
            return task
        except Task.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("No Task matches the given query.")

    # Create task in personal or collaborative list
    def perform_create(self, serializer):
        collab_list_id = self.request.data.get('collaborative_list_id')
        user_profile = self.request.user.profile
        
        try:
            if collab_list_id:
                extra_data = TaskService.create_in_collaborative_list(
                    collab_list_id=collab_list_id,
                    user_profile=user_profile,
                    task_data=serializer.validated_data
                )
            else:
                extra_data = TaskService.create_personal_task(user_profile)
            
            serializer.save(**extra_data)
            
        except (ValidationError, PermissionDenied):
            raise
    
    # Update and delete with ownership check
    def perform_update(self, serializer):
        instance = self.get_object()
        TaskService.check_task_ownership(instance, self.request.user.profile)
        serializer.save()

    # Delete with ownership check
    def perform_destroy(self, instance):
        TaskService.check_task_ownership(instance, self.request.user.profile)
        TaskService.delete_task(instance)

    # Restore soft-deleted task
    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        try:
            task = TaskService.restore_task(pk)
            TaskService.check_task_ownership(task, request.user.profile)
            
            serializer = self.get_serializer(task)
            return Response(serializer.data)
            
        except ObjectDoesNotExist:
            return Response(
                {"error": "Task not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


""" Authentication and User Management Endpoints
These endpoints handle user signup, login, logout, profile updates, and password recovery."""

# Get current user info
@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)

# signup endpoint
@api_view(["POST"])
def signup(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not all([username, email, password]):
        return Response(
            {"error": "All fields are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user, token = UserService.signup(username, email, password)
        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )

    except serializers.ValidationError as e:
        messages = [str(msg) for msgs in e.detail.values() for msg in msgs]
        return Response(
            {"error": " ".join(messages)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# login endpoint
@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not all([username, password]):
        return Response(
            {"error": "Username and password are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    user, token = UserService.login(username, password)
    if not user or not token:
        return Response(
            {"error": "Invalid credentials"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    return Response({
        "token": token.key,
        "user": UserSerializer(user).data
    })


# logout endpoint
@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    success = UserService.logout(request.user)
    if not success:
        return Response(
            {"warning": "No active token found"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response({"success": "Logged out successfully"})

# get security question endpoint
@api_view(["POST"])
def get_security_question(request):
    username = request.data.get("username")
    if not username:
        return Response(
            {"error": "Username is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    question = UserService.get_security_question(username)
    if not question:
        return Response(
            {"error": "User not found or no security question set"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({"security_question": question})

# verify security answer endpoint
@api_view(["POST"])
def verify_security_answer(request):
    username = request.data.get("username")
    security_answer = request.data.get("security_answer")

    if not all([username, security_answer]):
        return Response(
            {"error": "Username and answer required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        UserService.verify_security_answer(username, security_answer)
        return Response({"success": "Answer correct"})
        
    except ValidationError as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# reset password endpoint
@api_view(["POST"])
def reset_password(request):
    username = request.data.get("username")
    security_answer = request.data.get("security_answer")
    new_password = request.data.get("new_password")

    if not all([username, security_answer, new_password]):
        return Response(
            {"error": "All fields are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = UserService.verify_security_answer(username, security_answer)
        UserService.reset_password(user, new_password)
        return Response({"success": "Password has been reset"})
        
    except ValidationError as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

""" Profile Update Endpoints
These endpoints allow users to update their security questions and personal information."""

# update security question endpoint
@api_view(["PATCH"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_security_question(request):
    serializer = SetSecurityQuestionSerializer(data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)

    UserService.set_security_question(
        user=request.user,
        question=serializer.validated_data.get("security_question"),
        answer=serializer.validated_data.get("security_answer")
    )
    return Response(
        {"success": "Security question and answer updated successfully"},
        status=status.HTTP_200_OK
    )

# update user info endpoint
@api_view(["PATCH"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    data = request.data

    has_update = any([
        data.get("username"),
        data.get("email"),
        (data.get("old_password") and data.get("new_password"))
    ])
    
    if not has_update:
        return Response(
            {"error": "No valid fields provided for update"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    updated_fields = UserService.update_user(
        request.user,
        username=data.get("username"),
        email=data.get("email"),
        old_password=data.get("old_password"),
        new_password=data.get("new_password"),
    )
    return Response({
        "success": "Profile updated successfully",
        "updated_fields": updated_fields
    })

# change password endpoint  
@api_view(["PATCH"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not all([old_password, new_password]):
        return Response(
            {"error": "Both old and new password are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        success = UserService.change_password(request.user, old_password, new_password)
        if not success:
            return Response(
                {"error": "Old password is incorrect"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"success": "Password changed successfully"})
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

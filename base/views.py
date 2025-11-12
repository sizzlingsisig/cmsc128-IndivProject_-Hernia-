from django.forms import ValidationError
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist
from .serializers import (
    UserSerializer,
    TaskSerializer,
    SetSecurityQuestionSerializer,
)
from rest_framework.exceptions import PermissionDenied, ValidationError
from .serializers import CollaborativeListSerializer

from .models import Task, CollaborativeList
from .services.user_service import UserService
from .services.task_service import TaskService
from rest_framework import serializers
from django.contrib.auth.decorators import login_required
from django.db.models import Q

class CollaborativeListViewSet(viewsets.ModelViewSet):
    serializer_class = CollaborativeListSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "profile"):
            return CollaborativeList.objects.none()
        
        return CollaborativeList.objects.filter(
            Q(owner=user.profile) | Q(members=user.profile)
        ).distinct()
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)
    
    @action(detail=True, methods=['post'])  
    def add_member(self, request, pk=None):
        collab_list = self.get_object()
        if collab_list.owner != request.user.profile:
            return Response({"error": "Only owner can add members"}, status=403)
        
        username = request.data.get('username')
        if not username:
            return Response({"error": "Username required"}, status=400)
        
        try:
            user = User.objects.get(username=username)
            if not hasattr(user, 'profile'):
                return Response({"error": "User has no profile"}, status=404)
            
            collab_list.members.add(user.profile)
            return Response({"success": f"Added {username} to list"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


# ---------------- Home ----------------
def tasks(request):
    tasks = Task.objects.all()
    return render(request, "base/tasks.html", {"tasks": tasks})

def auth(request):
    return render(request, "base/auth.html")

def profile(request):
    return render(request, "base/profile.html")


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, "profile"):
            return Task.objects.none()
        
        view_type = self.request.query_params.get('view', 'personal')
        
        if view_type == 'collaborative':
            accessible_lists = CollaborativeList.objects.filter(
                Q(owner=user.profile) | Q(members=user.profile)
            )
            
            list_id = self.request.query_params.get('list_id')
            
            if list_id:
                # Filter by specific list
                return Task.objects.filter(
                    collaborative_list_id=list_id,
                    collaborative_list__in=accessible_lists  # Security check
                )
            else:
                # Return all accessible tasks
                return Task.objects.filter(collaborative_list__in=accessible_lists)
        else:
            return Task.objects.filter(
                profile=user.profile,
                collaborative_list__isnull=True
            )

    def perform_create(self, serializer):
        """Create task in personal or collaborative list"""
        collab_list_id = self.request.data.get('collaborative_list_id')
        
        if collab_list_id:
            # Creating in collaborative list
            try:
                collab_list = CollaborativeList.objects.get(id=collab_list_id)
                # Check if user has access
                if (collab_list.owner != self.request.user.profile and 
                    self.request.user.profile not in collab_list.members.all()):
                    raise PermissionDenied("No access to this list")
                
                serializer.save(collaborative_list=collab_list, created_by=self.request.user.profile)
            except CollaborativeList.DoesNotExist:
                raise ValidationError("Collaborative list not found")
        else:
            # Personal task
            serializer.save(profile=self.request.user.profile, created_by=self.request.user.profile)
            
    def perform_update(self, serializer):
        # Ensure user owns the task being edited
        instance = self.get_object()
        if instance.profile != self.request.user.profile:
            raise PermissionDenied("You cannot edit this task.")
        serializer.save()

    def perform_destroy(self, instance):
        # Ensure user owns the task being deleted
        if instance.profile != self.request.user.profile:
            raise PermissionDenied("You cannot delete this task.")
        instance.delete()

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        """
        Optional: restore soft-deleted task, but only if it belongs to current user.
        """
        try:
            task = TaskService.restore_task(pk)
            if task.profile != request.user.profile:
                raise PermissionDenied("You cannot restore this task.")
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "Task not found."}, status=404)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=403)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response(UserSerializer(user).data)

@api_view(["POST"])
def signup(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    if not username or not email or not password:
        return Response({"error": "All fields are required."}, status=400)

    try:
        user, token = UserService.signup(username, email, password)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    except serializers.ValidationError as e:
        messages = [str(msg) for msgs in e.detail.values() for msg in msgs]
        return Response({"error": " ".join(messages)}, status=400)

@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=400)

    user, token = UserService.login(username, password)
    if not user or not token:
        return Response({"error": "Invalid credentials."}, status=401)

    return Response({"token": token.key, "user": UserSerializer(user).data})

@api_view(["POST"])
def verify_security_answer(request):
    username = request.data.get("username")
    security_answer = request.data.get("security_answer")

    if not username or not security_answer:
        return Response({"error": "Username and answer required"}, status=400)

    user = User.objects.filter(username=username).first()
    if not user or not hasattr(user, "profile"):
        return Response({"error": "User not found"}, status=404)

    if user.profile.security_answer.strip().lower() != security_answer.strip().lower():
        return Response({"error": "Incorrect security answer"}, status=400)

    return Response({"success": "Answer correct"})

@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    success = UserService.logout(request.user)
    if not success:
        return Response({"warning": "No active token found."}, status=400)
    return Response({"success": "Logged out successfully."})


@api_view(["POST"])
def get_security_question(request):
    username = request.data.get("username")
    if not username:
        return Response({"error": "Username is required."}, status=400)

    question = UserService.get_security_question(username)
    if not question:
        return Response({"error": "User not found or no security question set."}, status=404)

    return Response({"security_question": question})


@api_view(["POST"])
def reset_password(request):
    username = request.data.get("username")
    security_answer = request.data.get("security_answer")
    new_password = request.data.get("new_password")

    if not username or not security_answer or not new_password:
        return Response({"error": "All fields are required."}, status=400)

    user = User.objects.filter(username=username).first()
    if not user or not hasattr(user, "profile"):
        return Response({"error": "User not found."}, status=404)

    if user.profile.security_answer.strip().lower() != security_answer.strip().lower():
        return Response({"error": "Incorrect security answer."}, status=400)

    UserService.reset_password(user, new_password)
    return Response({"success": "Password has been reset."})

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
    return Response({"success": "Security question and answer updated successfully."}, status=status.HTTP_200_OK)

@api_view(["PATCH"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    user = request.user
    data = request.data

    if not any([data.get("username"), data.get("email"), (data.get("old_password") and data.get("new_password"))]):
        return Response({"error": "No valid fields provided for update."}, status=400)

    updated_fields = UserService.update_user(
        user,
        username=data.get("username"),
        email=data.get("email"),
        old_password=data.get("old_password"),
        new_password=data.get("new_password"),
    )
    return Response({"success": "Profile updated successfully.", "updated_fields": updated_fields})


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):   
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not old_password or not new_password:
        return Response({"error": "Both old and new password are required."}, status=400)

    try:
        success = UserService.change_password(user, old_password, new_password)
        if not success:
            return Response({"error": "Old password is incorrect."}, status=400)
        return Response({"success": "Password changed successfully."})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"success": "Token valid!"})

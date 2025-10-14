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
from .models import Task
from .services.user_service import UserService
from .services.task_service import TaskService


# ---------------- Home ----------------
def home(request):
    tasks = Task.objects.all()
    return render(request, "base/home.html", {"tasks": tasks})

def auth(request):
    return render(request, "base/auth.html")

def profile(request):
    return render(request, "base/profile.html")


# ---------------- TaskViewSet ----------------
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        include_deleted = self.request.query_params.get("deleted", "false").lower() == "true"
        return Task.global_objects.all() if include_deleted else Task.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            TaskService.delete_task(self.get_object())
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({"error": "Task not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        try:
            task = TaskService.restore_task(pk)
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "Task not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


# ---------------- User Views ----------------
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
        }, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)


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


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"success": "Token valid!"})

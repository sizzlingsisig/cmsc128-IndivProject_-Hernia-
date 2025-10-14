from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .serializers import (
    UserSerializer,
    TaskSerializer,
    SecurityQuestionSerializer,
    SetSecurityQuestionSerializer,
    ResetPasswordSerializer
)
from .models import Task
from .services.user_service import UserService
from .services.task_service import TaskService


# ---------------- Home ----------------
def home(request):
    tasks = Task.objects.all()
    return render(request, "base/home.html", {"tasks": tasks})


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
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        try:
            task = TaskService.restore_task(pk)
            serializer = self.get_serializer(task)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------- User Views ----------------
@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = UserService.create_token(user)  # create token in service
        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=False)  # we don't need full serializer validation here

    try:
        user, token = UserService.login(
            username=request.data.get("username"),
            password=request.data.get("password")
        )
        user_data = UserSerializer(user).data
        return Response({"token": token.key, "user": user_data})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    success = UserService.logout(request.user)
    if not success:
        return Response({"warning": "No active token found."}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"success": "Logged out successfully."})


@api_view(["POST"])
def get_security_question(request):
    serializer = SecurityQuestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        question = UserService.get_security_question(serializer.validated_data["username"])
        return Response({"security_question": question})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        UserService.reset_password(
            username=serializer.validated_data["username"],
            security_answer=serializer.validated_data["security_answer"],
            new_password=serializer.validated_data["new_password"]
        )
        return Response({"success": "Password has been reset."})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def set_security_question(request):
    serializer = SetSecurityQuestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    UserService.set_security_question(
        user=request.user,
        question=serializer.validated_data["security_question"],
        answer=serializer.validated_data["security_answer"]
    )
    return Response({"success": "Security question and answer set successfully."})


@api_view(["PATCH"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def update_user_info(request):
    serializer = UserSerializer(instance=request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"success": "Profile updated successfully.", "updated_fields": serializer.validated_data})


@api_view(["GET"])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"success": "Token valid!"})

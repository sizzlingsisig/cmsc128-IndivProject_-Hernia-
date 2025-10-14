from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db import transaction
from ..models import Profile
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from ..serializers import UserSerializer

class UserService:

    @staticmethod
    @transaction.atomic
    def signup(username, email, password):
        # Use serializer to validate unique username/email and password length
        serializer = UserSerializer(data={"username": username, "email": email, "password": password})
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        Profile.objects.create(user=user)
        token = Token.objects.create(user=user)
        return user, token

    @staticmethod
    def login(username, password):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise ValidationError("Invalid credentials")

        if not user.check_password(password):
            raise ValidationError("Invalid credentials")

        token, _ = Token.objects.get_or_create(user=user)
        return user, token

    @staticmethod
    def logout(user):
        deleted_count, _ = Token.objects.filter(user=user).delete()
        return deleted_count > 0

    @staticmethod
    def get_security_question(username):
        try:
            user = User.objects.get(username=username)
            profile = user.profile
        except (User.DoesNotExist, ObjectDoesNotExist):
            raise ValidationError("User not found or no security question set.")

        if not profile.security_question:
            raise ValidationError("No security question set.")

        return profile.security_question

    @staticmethod
    def reset_password(username, security_answer, new_password):
        try:
            user = User.objects.get(username=username)
            profile = user.profile
        except (User.DoesNotExist, ObjectDoesNotExist):
            raise ValidationError("User not found.")

        if profile.security_answer.strip().lower() != security_answer.strip().lower():
            raise ValidationError("Incorrect security answer.")

        user.set_password(new_password)
        user.save()

    @staticmethod
    def set_security_question(user, question, answer):
        if not question or not answer:
            raise ValidationError("Both question and answer are required.")

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.security_question = question
        profile.security_answer = answer
        profile.save()

    @staticmethod
    def update_user(user, username=None, email=None, old_password=None, new_password=None):
        data = {}
        if username:
            data["username"] = username
        if email:
            data["email"] = email
        if old_password and new_password:
            if not user.check_password(old_password):
                raise ValidationError("Old password is incorrect.")
            user.set_password(new_password)
            data["password"] = "Password updated"

        if not data:
            raise ValidationError("No valid fields provided for update.")

        # Validate username/email uniqueness using serializer
        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return data

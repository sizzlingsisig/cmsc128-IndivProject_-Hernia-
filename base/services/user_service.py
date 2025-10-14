from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db import transaction
from ..models import Profile
from ..serializers import UserSerializer


class UserService:

    @staticmethod
    @transaction.atomic
    def signup(username, email, password):
        serializer = UserSerializer(data={
            "username": username,
            "email": email,
            "password": password
        })
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        return user, token

    @staticmethod
    def login(username, password):
        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            return None, None
        token, _ = Token.objects.get_or_create(user=user)
        return user, token

    @staticmethod
    def logout(user):
        deleted_count, _ = Token.objects.filter(user=user).delete()
        return deleted_count > 0

    @staticmethod
    def get_security_question(username):
        user = User.objects.filter(username=username).first()
        if not user or not hasattr(user, "profile"):
            return None
        return user.profile.security_question

    @staticmethod
    def reset_password(user, new_password):
        user.set_password(new_password)
        user.save()

    @staticmethod
    def set_security_question(user, question, answer):
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
            if user.check_password(old_password):
                user.set_password(new_password)
                data["password"] = "Password updated"

        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return data

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from ..models import Profile
from ..serializers import UserSerializer


class UserService:
    """Business logic for user operations"""

    @staticmethod
    @transaction.atomic
    def signup(username, email, password):
        """Create new user account with token"""
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
        """Authenticate user and return token"""
        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            return None, None
        
        token, _ = Token.objects.get_or_create(user=user)
        return user, token

    @staticmethod
    def logout(user):
        """Delete user's authentication token"""
        deleted_count, _ = Token.objects.filter(user=user).delete()
        return deleted_count > 0

    @staticmethod
    def get_security_question(username):
        """Retrieve security question for username"""
        user = User.objects.filter(username=username).first()
        if not user or not hasattr(user, "profile"):
            return None
        return user.profile.security_question

    @staticmethod
    def verify_security_answer(username, security_answer):
        """
        Verify security answer for a user
        
        Returns:
            User object if verification successful
            
        Raises:
            ValidationError: If user not found or answer incorrect
        """
        user = User.objects.filter(username=username).first()
        if not user or not hasattr(user, "profile"):
            raise ValidationError("User not found")

        if user.profile.security_answer.strip().lower() != security_answer.strip().lower():
            raise ValidationError("Incorrect security answer")

        return user

    @staticmethod
    def reset_password(user, new_password):
        """Reset user password"""
        user.set_password(new_password)
        user.save()

    @staticmethod
    def set_security_question(user, question, answer):
        """Set or update security question and answer"""
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.security_question = question
        profile.security_answer = answer
        profile.save()

    @staticmethod
    def update_user(user, username=None, email=None, old_password=None, new_password=None):
        """Update user profile information"""
        data = {}
        
        if username:
            data["username"] = username
        if email:
            data["email"] = email
        if old_password and new_password and user.check_password(old_password):
            user.set_password(new_password)
            data["password"] = "Password updated"

        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return data
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """Change password with old password verification"""
        if not user.check_password(old_password):
            return False
        
        user.set_password(new_password)
        user.save()
        return True

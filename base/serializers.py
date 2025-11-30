from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from .models import Task, Profile, CollaborativeList

class TaskSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.user.username', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_datetime', 'priority', 'status', 'created_at', 'updated_at', 'created_by_username']
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by_username')


class CollaborativeListSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.user.username', read_only=True)
    member_usernames = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CollaborativeList
        fields = ['id', 'name', 'owner', 'owner_username', 'members', 'member_usernames', 'task_count', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']
    
    def get_member_usernames(self, obj):
        return [member.user.username for member in obj.members.all()]
    
    def get_task_count(self, obj):
        return obj.tasks.count()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['security_question', 'security_answer', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True},  
        }

    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Username already taken.")]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email already in use.")]
    )
    password = serializers.CharField(write_only=True, required=True, min_length=6 ,error_messages={
        'required': 'Password is required.',
        'min_length': 'Password must be at least 6 characters long.'
    })

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        Profile.objects.create(user=user) 
        return user

    def update(self, instance, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        password = validated_data.get('password')

        if username:
            instance.username = username
        if email:
            instance.email = email
        if password:
            instance.set_password(password)

        instance.save()
        return instance

class SecurityQuestionSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

class SetSecurityQuestionSerializer(serializers.Serializer):
    security_question = serializers.CharField(required=True)
    security_answer = serializers.CharField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    security_answer = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)

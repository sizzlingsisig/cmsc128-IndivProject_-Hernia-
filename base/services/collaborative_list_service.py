from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.exceptions import ValidationError, PermissionDenied

from ..models import CollaborativeList


class CollaborativeListService:
    """Business logic for collaborative list operations"""
    
    @staticmethod
    def get_accessible_lists(profile):
        """Get all collaborative lists accessible to a user"""
        return CollaborativeList.objects.filter(
            Q(owner=profile) | Q(members=profile)
        ).distinct()
    
    @staticmethod
    def add_member(collab_list, username, requester_profile):
        """
        Add a member to a collaborative list
        Raises:
            PermissionDenied: If requester is not the owner
            ValidationError: If username is invalid
            ObjectDoesNotExist: If user not found
        """
        # Check ownership
        if collab_list.owner != requester_profile:
            raise PermissionDenied("Only owner can add members")
        
        # Validate username
        if not username:
            raise ValidationError("Username required")
        
        try:
            user = User.objects.get(username=username)
            
            if not hasattr(user, 'profile'):
                raise ValidationError("User has no profile")
            
            # Add member
            collab_list.members.add(user.profile)
            return user.profile
            
        except User.DoesNotExist:
            raise ObjectDoesNotExist("User not found")

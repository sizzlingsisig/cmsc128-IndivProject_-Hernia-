from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CollaborativeListViewSet, home, auth, TaskViewSet,
    profile, signup, login, test_token,
    get_security_question, reset_password, update_security_question,
    update_user_info, logout, verify_security_answer , me, change_password
)

# Router for tasks
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'collaborative-lists', CollaborativeListViewSet, basename='collaborative-list')

# User endpoint patterns grouped under /api/users/
user_patterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('test-token/', test_token, name='test-token'),
    path('get-security-question/', get_security_question, name='get-security-question'),
    path('reset-password/', reset_password, name='reset-password'),
    path('update-security-question/', update_security_question, name='update-security-question'),
    path('update-user-info/', update_user_info, name='update-user-info'),
    path('logout/', logout, name='logout'),
    path('verify-security-answer/', verify_security_answer, name='verify-security-answer'),
    path('change-password/', change_password, name='change-password'),
    path('me/', me, name='me'),  
]

urlpatterns = [
    # Home
    path('', auth, name='auth'),
    path('home/', home, name='home'),
    path('profile/', profile, name='profile'),

    path('api/', include([
        path('', include(router.urls)),
        path('users/', include(user_patterns)),
    ])),
]

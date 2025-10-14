from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    home, auth, TaskViewSet,
    profile, signup, login, test_token,
    get_security_question, reset_password, update_security_question,
    update_user_info, logout
)

# Router for tasks
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

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

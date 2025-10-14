from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    home, TaskViewSet,
    signup, login, test_token,
    get_security_question, reset_password,
    update_user_info, set_security_question, logout
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
    path('set-security-question/', set_security_question, name='set-security-question'),
    path('update-user-info/', update_user_info, name='update-user-info'),
    path('logout/', logout, name='logout'),
]

urlpatterns = [
    # Home
    path('', home, name='home'),

    # API routes
    path('api/', include([
        # Task routes under /api/tasks/
        path('', include(router.urls)),

        # User routes under /api/users/
        path('users/', include(user_patterns)),
    ])),
]

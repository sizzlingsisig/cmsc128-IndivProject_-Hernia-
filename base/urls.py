from django.urls import path, include
from .views import home, TaskViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', home, name='home'),

    path('api/', include(router.urls)),
]

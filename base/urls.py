from django.urls import path
from . import views
from .views import TaskListCreate, TaskDetail

urlpatterns = [
    path('', views.home, name='home'),
    path('tasks/', TaskListCreate.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
]
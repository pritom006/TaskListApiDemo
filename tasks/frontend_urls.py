from django.urls import path
from .views import login_view, signup_view, tasks_view, task_detail_view

urlpatterns = [
    path('', login_view, name='login'),  # Root URL shows login page
    path('signup/', signup_view, name='signup'),
    path('tasks/', tasks_view, name='tasks'),
    path('task-detail/', task_detail_view, name='task-detail'),
]
from django.urls import path
from .views import TaskListCreateAPIView, TaskDetailAPIView, SignUpView, CustomTokenObtainPairView, LogoutView
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='api-signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='api-login'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='api-token_refresh'),
    path('logout/', LogoutView.as_view(), name='api-logout'),
    path('tasks/', TaskListCreateAPIView.as_view(), name='api-task-list-create'),
    path('tasks/<int:pk>/', TaskDetailAPIView.as_view(), name='api-task-detail'),
]
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer, UserSerializer
from rest_framework.permissions import BasePermission
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.views import View


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                # Create token and return it along with user data
                return Response(
                    {
                        "user": UserSerializer(user).data,
                        "message": "User Created Successfully"
                    },
                    status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = get_user_model().objects.get(username=request.data['username'])
            response.data['user'] = {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        return response


# class HomeView(View):
#     def get(self, request):
#         return render(request, 'login.html')

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def tasks_view(request):
    return render(request, 'tasks.html')

def task_detail_view(request):
    return render(request, 'task_detail.html')

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Invalid token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class IsLead(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'lead'

class IsDeveloper(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'developer'

class TaskListCreateAPIView(APIView):
    permission_classes = [IsLead | IsDeveloper]  # Both leads and developers can access

    def get(self, request):
        if request.user.role == 'lead':
            tasks = Task.objects.all()
        else:
            tasks = Task.objects.filter(developer=request.user)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role == 'developer':
            request.data['developer'] = request.user.id  # Ensure developer is linked to task
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    permission_classes = [IsLead | IsDeveloper]

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            if request.user.role == 'developer' and task.developer != request.user:
                return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            if request.user.role == 'developer' and task.developer != request.user:
                return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
            if request.user.role == 'developer' and task.developer != request.user:
                return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
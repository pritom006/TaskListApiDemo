from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock, PropertyMock, MagicMock
from django.contrib.auth import get_user_model
from ..models import Task
from ..serializers import TaskSerializer, UserSerializer
import json
from rest_framework.response import Response
from tasks.serializers import TaskSerializer
User = get_user_model()

class MockUser:
    def __init__(self, id=1, username="testuser", role="developer"):
        self.id = id
        self.username = username
        self.role = role
        self.is_authenticated = True

class TestSignUpView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('api-signup')
        self.user_data = {
            "username": "testuser",
            "password": "testpass123",
            "role": "developer"
        }

    @patch('tasks.serializers.UserSerializer.is_valid')
    @patch('tasks.serializers.UserSerializer.save')
    def test_successful_signup(self, mock_save, mock_is_valid):
        mock_is_valid.return_value = True
        mock_user = MockUser()
        mock_save.return_value = mock_user

        response = self.client.post(self.signup_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_is_valid.assert_called_once()
        mock_save.assert_called_once()

    @patch('tasks.serializers.UserSerializer.is_valid')
    @patch('tasks.serializers.UserSerializer.errors', new_callable=PropertyMock)
    def test_invalid_signup(self, mock_errors, mock_is_valid):
        mock_is_valid.return_value = False
        mock_errors.return_value = {"username": ["This field is required."]}  # Mock validation errors

        response = self.client.post(self.signup_url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_is_valid.assert_called_once()

class TestCustomTokenObtainPairView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('api-login')
        self.user_data = {
            "username": "testuser",
            "password": "testpass123"
        }

    @patch('tasks.views.TokenObtainPairView.post')
    @patch('tasks.views.get_user_model')
    def test_successful_login(self, mock_get_user_model, mock_token_view_post):
        mock_response_data = {
            'access': 'dummy_token',
            'refresh': 'dummy_refresh'
        }
        mock_response = Response(data=mock_response_data, status=status.HTTP_200_OK)
        mock_token_view_post.return_value = mock_response

        mock_user = MockUser()
        mock_user_model = Mock()
        mock_user_model.objects.get.return_value = mock_user
        mock_get_user_model.return_value = mock_user_model

        response = self.client.post(self.login_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)

class TestLogoutView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.logout_url = reverse('api-logout')
        self.refresh_token = {"refresh": "dummy_refresh_token"}

    @patch('tasks.views.RefreshToken')
    def test_successful_logout(self, mock_refresh_token):
        self.client.force_authenticate(user=MockUser())
        
        mock_token = Mock()
        mock_refresh_token.return_value = mock_token

        response = self.client.post(self.logout_url, self.refresh_token, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_token.blacklist.assert_called_once()

    def test_logout_without_authentication(self):
        response = self.client.post(self.logout_url, self.refresh_token, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('tasks.views.RefreshToken')
    def test_logout_with_invalid_token(self, mock_refresh_token):
        self.client.force_authenticate(user=MockUser())
        
        # Make RefreshToken raise an exception when initialized
        mock_refresh_token.side_effect = Exception("Invalid token")

        response = self.client.post(self.logout_url, self.refresh_token, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Invalid token"})
        
class TestTaskListCreateAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.tasks_url = reverse('api-task-list-create')
        self.mock_task_data = {
            "title": "Test Task",
            "description": "Test Description"
        }

    @patch('tasks.views.TaskSerializer')
    @patch('tasks.models.Task.objects')
    def test_get_tasks_as_lead(self, mock_task_objects, mock_serializer_class):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        mock_tasks = [
            Mock(id=1, title='Task 1'),
            Mock(id=2, title='Task 2')
        ]
        
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__iter__.return_value = iter(mock_tasks)
        type(mock_queryset).count = PropertyMock(return_value=len(mock_tasks))
        
        mock_task_objects.all.return_value = mock_queryset

        mock_serializer = Mock()
        mock_serializer.data = [
            {'id': 1, 'title': 'Task 1'},
            {'id': 2, 'title': 'Task 2'}
        ]
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(self.tasks_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_task_objects.all.assert_called_once()

    @patch('tasks.views.TaskSerializer')
    @patch('tasks.models.Task.objects')
    def test_get_tasks_as_developer(self, mock_task_objects, mock_serializer_class):
        dev_user = MockUser(role="developer")
        self.client.force_authenticate(user=dev_user)

        mock_tasks = [
            Mock(id=1, title='Task 1')
        ]
        
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__iter__.return_value = iter(mock_tasks)
        type(mock_queryset).count = PropertyMock(return_value=len(mock_tasks))
        
        mock_task_objects.filter.return_value = mock_queryset

        mock_serializer = Mock()
        mock_serializer.data = [{'id': 1, 'title': 'Task 1'}]
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(self.tasks_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_task_objects.filter.assert_called_once_with(developer=dev_user)


    @patch('tasks.views.TaskSerializer')
    def test_create_task_as_developer(self, mock_serializer_class):
        dev_user = MockUser(role="developer")
        self.client.force_authenticate(user=dev_user)

        mock_serializer = Mock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = {
            'id': 1,
            'title': 'Test Task',
            'description': 'Test Description'
        }
        mock_serializer_class.return_value = mock_serializer

        response = self.client.post(self.tasks_url, self.mock_task_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_serializer.is_valid.assert_called_once()
        mock_serializer.save.assert_called_once()
    
    @patch('tasks.views.TaskSerializer')
    def test_create_task_as_lead_forbidden(self, mock_serializer_class):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)
        
        response = self.client.post(self.tasks_url, self.mock_task_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"error": "Leads cannot create tasks"})
    
    @patch('tasks.views.TaskSerializer')
    @patch('tasks.models.Task.objects')
    def test_get_task_filter_by_status(self, mock_task_objects, mock_serializer_class):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        mock_tasks = [Mock(id=1, title='Task 1', is_done=True)]
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__iter__.return_value = iter(mock_tasks)
        mock_task_objects.all.return_value = mock_queryset

        mock_serializer = Mock()
        mock_serializer.data = [{'id': 1, 'title': 'Task 1', 'is_done': True}]
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(f'{self.tasks_url}?is_done=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_task_objects.all.assert_called_once()
        mock_queryset.filter.assert_called_with(is_done=True)
    
    @patch('tasks.views.TaskSerializer')
    @patch('tasks.models.Task.objects')
    def test_pagination(self, mock_task_objects, mock_serializer_class):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        mock_tasks = [Mock(id=i, title=f'Task {i}') for i in range(1, 15)]
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__iter__.return_value = iter(mock_tasks[:10])
        mock_task_objects.all.return_value = mock_queryset

        mock_serializer = Mock()
        mock_serializer.data = [{'id': t.id, 'title': t.title} for t in mock_tasks[:10]]
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(f'{self.tasks_url}?page=1&page_size=10')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    @patch('tasks.views.TaskSerializer')
    @patch('tasks.models.Task.objects')
    def test_get_task_filter_by_developer(self, mock_task_objects, mock_serializer_class):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        mock_tasks = [Mock(id=1, title='Task 1', developer_id=5)]
        mock_queryset = MagicMock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__iter__.return_value = iter(mock_tasks)
        mock_task_objects.all.return_value = mock_queryset

        mock_serializer = Mock()
        mock_serializer.data = [{'id': 1, 'title': 'Task 1', 'developer_id': 5}]
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(f'{self.tasks_url}?developer=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_task_objects.all.assert_called_once()
        mock_queryset.filter.assert_called_with(developer_id='5')

    @patch('tasks.views.TaskSerializer')
    @patch('tasks.models.Task.objects')
    def test_get_task_filter_by_lead(self, mock_task_objects, mock_serializer_class):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        mock_tasks = [Mock(id=1, title='Task 1')]
        mock_queryset = MagicMock()
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__iter__.return_value = iter(mock_tasks)
        mock_task_objects.all.return_value = mock_queryset

        mock_serializer = Mock()
        mock_serializer.data = [{'id': 1, 'title': 'Task 1'}]
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(self.tasks_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_task_objects.all.assert_called_once()


class TestTaskDetailAPIView(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.task_id = 1
        self.task_url = reverse('api-task-detail', args=[self.task_id])

    @patch('tasks.models.Task.objects')
    def test_delete_task_as_lead(self, mock_task_objects):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        mock_task = Mock()
        mock_task.id = 1
        mock_task.title = "Task 1"
        mock_task.developer = None  
        mock_task.delete = Mock()

        mock_task_objects.get.return_value = mock_task

        response = self.client.delete(self.task_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_task_objects.get.assert_called_once_with(pk=self.task_id)
        mock_task.delete.assert_not_called()
        self.assertEqual(response.data, {"error": "Leads cannot delete tasks"})

    @patch('tasks.views.TaskSerializer')
    @patch('tasks.models.Task.objects')
    def test_update_task_as_developer(self, mock_task_objects, mock_serializer_class):
        dev_user = MockUser(role="developer")
        self.client.force_authenticate(user=dev_user)

        mock_task = Mock()
        mock_task.id = 1
        mock_task.title = "Task 1"
        mock_task.developer = dev_user
        mock_task_objects.get.return_value = mock_task

        mock_serializer = Mock()
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = {'id': 1, 'title': 'Updated Task', 'is_done': True}
        mock_serializer_class.return_value = mock_serializer

        update_data = {"title": "Updated Task", "is_done": True}
        response = self.client.put(self.task_url, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_serializer.is_valid.assert_called_once()
        mock_serializer.save.assert_called_once()

    @patch('tasks.models.Task.objects')
    def test_task_not_found(self, mock_task_objects):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        mock_task_objects.get.side_effect = Task.DoesNotExist

        response = self.client.get(self.task_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('tasks.models.Task.objects')
    def test_developer_access_denied(self, mock_task_objects):
        dev_user = MockUser(role="developer")
        self.client.force_authenticate(user=dev_user)

        other_developer = MockUser(role="developer")
        mock_task = Mock()
        mock_task.id = 1
        mock_task.title = "Task 1"
        mock_task.developer = other_developer  
        mock_task_objects.get.return_value = mock_task

        response = self.client.get(self.task_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    @patch('tasks.models.Task.objects')
    def test_get_others_tasks_as_developer(self, mock_task_objects):
        dev_user = MockUser(role="developer")
        self.client.force_authenticate(user=dev_user)

        other_dev = MockUser(role="developer")
        mock_task = Mock(id=2, title="Other's Task", developer=other_dev)
        mock_task_objects.get.return_value = mock_task

        response = self.client.get(self.task_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_task_objects.get.assert_called_once_with(pk=self.task_id)
    

    @patch('tasks.views.TaskSerializer')
    @patch('tasks.models.Task.objects')
    def test_get_task_as_lead(self, mock_task_objects, mock_serializer_class):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        # Create a simple mock task
        mock_task = Mock()
        mock_task.id = 1
        mock_task.title = "Task for Lead"
        mock_task.description = "Test description"
        mock_task.status = "open"
        mock_task_objects.get.return_value = mock_task

        # Setup serializer mock
        mock_serializer = Mock()
        mock_serializer.data = {
            'id': 1,
            'title': "Task for Lead",
            'description': "Test description",
            'status': "open"
        }
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(self.task_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_task_objects.get.assert_called_once_with(pk=self.task_id)
        
        # Assert response data
        self.assertEqual(response.data['title'], "Task for Lead")
        self.assertEqual(response.data['id'], 1)


    @patch('tasks.views.TaskSerializer')
    @patch('tasks.models.Task.objects')
    def test_update_others_task_as_developer(self, mock_task_objects, mock_serializer_class):
        dev_user = MockUser(role="developer")
        self.client.force_authenticate(user=dev_user)

        other_dev = MockUser(role="developer")
        mock_task = Mock(id=2, title="Other's Task", developer=other_dev)
        mock_task_objects.get.return_value = mock_task

        update_data = {"title": "Updated Task"}
        response = self.client.put(self.task_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_task_objects.get.assert_called_once_with(pk=self.task_id)

    @patch('tasks.models.Task.objects')
    def test_update_task_as_lead_forbidden(self, mock_task_objects):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        mock_task = Mock(id=1, title="Task 1")
        mock_task_objects.get.return_value = mock_task

        update_data = {"title": "Updated Task"}
        response = self.client.put(self.task_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_task_objects.get.assert_called_once_with(pk=self.task_id)

    @patch('tasks.models.Task.objects')
    def test_delete_own_task_as_developer(self, mock_task_objects):
        dev_user = MockUser(role="developer")
        self.client.force_authenticate(user=dev_user)

        mock_task = Mock(id=1, title="Own Task", developer=dev_user)
        mock_task.delete = Mock()
        mock_task_objects.get.return_value = mock_task

        response = self.client.delete(self.task_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_task.delete.assert_called_once()

    @patch('tasks.models.Task.objects')
    def test_delete_other_task_as_developer(self, mock_task_objects):
        dev_user = MockUser(role="developer")
        self.client.force_authenticate(user=dev_user)

        other_dev = MockUser(role="developer")
        mock_task = Mock(id=2, title="Other's Task", developer=other_dev)
        mock_task_objects.get.return_value = mock_task

        response = self.client.delete(self.task_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_task_objects.get.assert_called_once_with(pk=self.task_id)

    @patch('tasks.models.Task.objects')
    def test_delete_task_as_lead_forbidden(self, mock_task_objects):
        lead_user = MockUser(role="lead")
        self.client.force_authenticate(user=lead_user)

        mock_task = Mock(id=1, title="Task 1")
        mock_task_objects.get.return_value = mock_task

        response = self.client.delete(self.task_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        mock_task_objects.get.assert_called_once_with(pk=self.task_id)




class TestUserListAPIView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.users_url = reverse('api-user-list')  
        
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='developer'
        )

    def test_get_users_unauthenticated(self):
        """Test that unauthenticated users cannot access the endpoint"""
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('tasks.views.UserSerializer')
    @patch('tasks.models.User.objects') 
    def test_get_all_users(self, mock_user_objects, mock_serializer_class):
        """Test getting all users without role filter"""
        self.client.force_authenticate(user=self.user)

        mock_user1 = Mock(id=1, username='user1', role='developer')
        mock_user2 = Mock(id=2, username='user2', role='lead')

        mock_users = [mock_user1, mock_user2]

        mock_user_objects.all.return_value = mock_users  

        mock_serializer = Mock()
        mock_serializer.data = [
            {'id': 1, 'username': 'user1', 'role': 'developer'},
            {'id': 2, 'username': 'user2', 'role': 'lead'}
        ]
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(self.users_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        mock_user_objects.all.assert_called_once()
        mock_serializer_class.assert_called_once_with(mock_users, many=True)

    @patch('tasks.views.UserSerializer')
    @patch('tasks.models.User.objects')  
    def test_get_users_filtered_by_role(self, mock_user_objects, mock_serializer_class):
        """Test getting users filtered by role"""
        self.client.force_authenticate(user=self.user)

        mock_user = Mock(id=1, username='user1', role='developer')
        mock_users = [mock_user]
        
        mock_user_objects.filter.return_value = mock_users

        mock_serializer = Mock()
        mock_serializer.data = [
            {'id': 1, 'username': 'user1', 'role': 'developer'}
        ]
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(f"{self.users_url}?role=developer")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        mock_user_objects.filter.assert_called_once_with(role='developer')
        mock_serializer_class.assert_called_once_with(mock_users, many=True)


    @patch('tasks.views.UserSerializer')
    @patch('tasks.models.User.objects')  
    def test_get_users_empty_result(self, mock_user_objects, mock_serializer_class):
        """Test getting users with filter that returns no results"""
        self.client.force_authenticate(user=self.user)

        mock_users = []
        mock_user_objects.filter.return_value = mock_users  # No users found

        mock_serializer = Mock()
        mock_serializer.data = []
        mock_serializer_class.return_value = mock_serializer

        response = self.client.get(f"{self.users_url}?role=nonexistent")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        mock_user_objects.filter.assert_called_once_with(role='nonexistent')
        mock_serializer_class.assert_called_once_with(mock_users, many=True)



    def test_get_users_invalid_method(self):
        """Test that only GET method is allowed"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(self.users_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(self.users_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
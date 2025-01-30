from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from tasks.models import Task
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.User = get_user_model()
        # Create test users
        self.developer = self.User.objects.create_user(
            username='testdev',
            password='testpass123',
            role='developer',
            is_active=True
        )
        self.lead = self.User.objects.create_user(
            username='testlead',
            password='testpass123',
            role='lead',
            is_active=True
        )
        self.another_developer = self.User.objects.create_user(
            username='anotherdev',
            password='testpass123',
            role='developer',
            is_active=True
        )
        
    def authenticate_user(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return refresh

class SignUpViewTests(APITestCase):
    def test_signup_success(self):
        url = reverse('api-signup')
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'role': 'developer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('message', response.data)
        
    def test_signup_duplicate_username(self):
        # Create first user
        self.client.post(reverse('api-signup'), {
            'username': 'newuser',
            'password': 'testpass123',
            'role': 'developer'
        })
        
        # Try to create duplicate user
        response = self.client.post(reverse('api-signup'), {
            'username': 'newuser',
            'password': 'anotherpass',
            'role': 'developer'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_signup_invalid_role(self):
        response = self.client.post(reverse('api-signup'), {
            'username': 'newuser',
            'password': 'testpass123',
            'role': 'invalid_role'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairViewTests(BaseAPITestCase):
    def test_token_obtain_pair(self):
        url = reverse('api-login')
        data = {
            'username': 'testdev',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testdev')
        
    def test_token_obtain_pair_invalid_credentials(self):
        url = reverse('api-login')
        data = {
            'username': 'testdev',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserListAPIViewTests(BaseAPITestCase):
    def test_get_users_list_authenticated(self):
        self.authenticate_user(self.developer)
        response = self.client.get(reverse('api-user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # All test users
        
    def test_get_users_by_role(self):
        self.authenticate_user(self.developer)
        response = self.client.get(f"{reverse('api-user-list')}?role=developer")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only developers
        
    def test_get_users_unauthenticated(self):
        response = self.client.get(reverse('api-user-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TaskListCreateAPIViewTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        # Create some tasks
        self.task1 = Task.objects.create(
            title='Dev Task 1',
            description='Description 1',
            developer=self.developer
        )
        self.task2 = Task.objects.create(
            title='Dev Task 2',
            description='Description 2',
            developer=self.developer,
            is_done=True
        )
        self.another_dev_task = Task.objects.create(
            title='Another Dev Task',
            description='Description 3',
            developer=self.another_developer
        )

    def test_get_tasks_as_developer(self):
        self.authenticate_user(self.developer)
        response = self.client.get(reverse('api-task-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only developer's tasks
        
    def test_get_tasks_as_lead(self):
        self.authenticate_user(self.lead)
        response = self.client.get(reverse('api-task-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # All tasks
        
    def test_get_tasks_filter_by_developer(self):
        self.authenticate_user(self.lead)
        response = self.client.get(f"{reverse('api-task-list-create')}?developer={self.developer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
    def test_get_tasks_filter_by_status(self):
        self.authenticate_user(self.developer)
        response = self.client.get(f"{reverse('api-task-list-create')}?is_done=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_create_task_as_developer(self):
        self.authenticate_user(self.developer)
        
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'developer': self.developer.id  
        }
        
        response = self.client.post(reverse('api-task-list-create'), data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['developer'], self.developer.id)
        created_task = Task.objects.get(id=response.data['id'])
        self.assertEqual(created_task.title, 'New Task')
        self.assertEqual(created_task.description, 'New Description')
        self.assertEqual(created_task.developer, self.developer)
        
    def test_create_task_as_lead_forbidden(self):
        self.authenticate_user(self.lead)
        data = {
            'title': 'New Task',
            'description': 'New Description'
        }
        response = self.client.post(reverse('api-task-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_pagination(self):
        # Create more tasks to test pagination
        for i in range(15):  # Creates 15 more tasks
            Task.objects.create(
                title=f'Task {i}',
                developer=self.developer
            )
        
        self.authenticate_user(self.developer)
        response = self.client.get(reverse('api-task-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # Default page size
        self.assertIsNotNone(response.data['next'])  # Should have next page
        self.assertIsNotNone(response.data['count'])

class TaskDetailAPIViewTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            developer=self.developer
        )

    def test_get_own_task_as_developer(self):
        self.authenticate_user(self.developer)
        response = self.client.get(reverse('api-task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Task')
        
    def test_get_others_task_as_developer(self):
        self.authenticate_user(self.another_developer)
        response = self.client.get(reverse('api-task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_get_task_as_lead(self):
        self.authenticate_user(self.lead)
        response = self.client.get(reverse('api-task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_update_own_task_as_developer(self):
        self.authenticate_user(self.developer)
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'is_done': True
        }
        response = self.client.put(
            reverse('api-task-detail', args=[self.task.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Task')
        self.assertTrue(response.data['is_done'])
        
    def test_update_others_task_as_developer(self):
        self.authenticate_user(self.another_developer)
        data = {
            'title': 'Updated Task'
        }
        response = self.client.put(
            reverse('api-task-detail', args=[self.task.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_update_task_as_lead_forbidden(self):
        self.authenticate_user(self.lead)
        data = {
            'title': 'Updated Task'
        }
        response = self.client.put(
            reverse('api-task-detail', args=[self.task.id]),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_own_task_as_developer(self):
        self.authenticate_user(self.developer)
        response = self.client.delete(reverse('api-task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_delete_others_task_as_developer(self):
        self.authenticate_user(self.another_developer)
        response = self.client.delete(reverse('api-task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_task_as_lead_forbidden(self):
        self.authenticate_user(self.lead)
        response = self.client.delete(reverse('api-task-detail', args=[self.task.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class LogoutViewTests(BaseAPITestCase):
    def test_logout_success(self):
        refresh = self.authenticate_user(self.developer)
        response = self.client.post(reverse('api-logout'), {'refresh': str(refresh)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_logout_invalid_token(self):
        self.authenticate_user(self.developer)
        response = self.client.post(reverse('api-logout'), {'refresh': 'invalid_token'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_logout_unauthenticated(self):
        response = self.client.post(reverse('api-logout'), {'refresh': 'some_token'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
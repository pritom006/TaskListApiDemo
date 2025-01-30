from rest_framework.test import APITestCase
from tasks.serializers import TaskSerializer, UserSerializer
from django.contrib.auth import get_user_model
from tasks.models import Task
from django.utils import timezone
from datetime import datetime

class UserSerializerTests(APITestCase):
    def test_serialize_user(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123',
            role='developer'
        )
        serializer = UserSerializer(user)
        data = serializer.data
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['role'], 'developer')
        self.assertNotIn('password', data)

    def test_deserialize_user_create(self):
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'role': 'developer'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.role, 'developer')
        self.assertTrue(user.check_password('newpass123'))

    def test_deserialize_user_invalid_role(self):
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'role': 'invalid_role'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('role', serializer.errors)

    def test_deserialize_user_missing_fields(self):
        data = {
            'username': 'newuser',
            'role': 'developer'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

class TaskSerializerTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testdev',
            password='testpass123',
            role='developer'
        )

    def test_serialize_task(self):
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            developer=self.user,
            is_done=True
        )
        serializer = TaskSerializer(task)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Task')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['developer'], self.user.id)
        self.assertEqual(data['developer_username'], self.user.username)
        self.assertTrue(data['is_done'])
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('completed_at', data)

    def test_deserialize_task_create(self):
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'developer': self.user.id
        }
        serializer = TaskSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        
        self.assertEqual(task.title, 'New Task')
        self.assertEqual(task.description, 'New Description')
        self.assertEqual(task.developer, self.user)

    def test_deserialize_task_update(self):
        task = Task.objects.create(
            title='Original Task',
            description='Original Description',
            developer=self.user
        )
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'is_done': True
        }
        serializer = TaskSerializer(task, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_task = serializer.save()
        
        self.assertEqual(updated_task.title, 'Updated Task')
        self.assertEqual(updated_task.description, 'Updated Description')
        self.assertTrue(updated_task.is_done)
        self.assertIsNotNone(updated_task.completed_at)

    def test_deserialize_task_invalid_developer(self):
        data = {
            'title': 'New Task',
            'description': 'New Description',
            'developer': 999  # Non-existent user ID
        }
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('developer', serializer.errors)

    def test_task_date_formatting(self):
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            developer=self.user,
            is_done=True
        )
        serializer = TaskSerializer(task)
        data = serializer.data
        
        # Check date format
        date_format = '%Y-%m-%d %H:%M:%S'
        try:
            datetime.strptime(data['created_at'], date_format)
            datetime.strptime(data['updated_at'], date_format)
            datetime.strptime(data['completed_at'], date_format)
        except ValueError:
            self.fail("Date format is incorrect")

    def test_serialize_task_without_developer(self):
        task = Task.objects.create(
            title='Test Task',
            description='Test Description'
        )
        serializer = TaskSerializer(task)
        data = serializer.data
        
        self.assertIsNone(data['developer'])
        self.assertIsNone(data['developer_username'])
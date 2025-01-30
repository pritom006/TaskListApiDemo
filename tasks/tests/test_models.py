from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from tasks.models import Task, User
from django.contrib.auth import get_user_model

class UserModelTests(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='developer'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'developer')
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password('testpass123'))

    def test_create_user_without_role(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_create_user_with_invalid_role(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            role="invalid"
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            role='lead'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_active)

    def test_user_str_method(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='developer'
        )
        self.assertEqual(str(user), 'testuser')

class TaskModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testdev',
            password='testpass123',
            role='developer'
        )

    def test_create_task_success(self):
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            developer=self.user
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'Test Description')
        self.assertEqual(task.developer, self.user)
        self.assertFalse(task.is_done)
        self.assertIsNone(task.completed_at)

    def test_task_completion_timestamp(self):
        task = Task.objects.create(
            title='Test Task',
            developer=self.user
        )
        self.assertIsNone(task.completed_at)
        
        # Mark as done
        task.is_done = True
        task.save()
        self.assertIsNotNone(task.completed_at)
        
        # Mark as not done
        task.is_done = False
        task.save()
        self.assertIsNone(task.completed_at)

    def test_task_auto_timestamps(self):
        task = Task.objects.create(
            title='Test Task',
            developer=self.user
        )
        original_created = task.created_at
        original_updated = task.updated_at
        
        # Wait a second to ensure timestamp difference
        from time import sleep
        sleep(1)
        
        task.title = 'Updated Task'
        task.save()
        
        self.assertEqual(task.created_at, original_created)
        self.assertGreater(task.updated_at, original_updated)

    def test_task_str_method(self):
        task = Task.objects.create(
            title='Test Task',
            developer=self.user
        )
        self.assertEqual(str(task), 'Test Task')

    def test_task_without_title(self):
        task = Task(
            description="test description",
            # user = self.user
        )
        with self.assertRaises(ValidationError):
            task.full_clean()
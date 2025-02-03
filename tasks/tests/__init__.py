# from django.contrib.auth import get_user_model

# def create_test_user(username="testuser", password="testpass123", role="developer", is_active=False):
#     User = get_user_model()
#     return User.objects.create_user(
#         username=username,
#         password=password,
#         role=role,
#         is_active=is_active
#     )

# def create_test_task(title="Test Task", description="Test Description", developer=None, is_done=False):
#     from tasks.models import Task
#     return Task.objects.create(
#         title=title,
#         description=description,
#         developer=developer,
#         is_done=is_done
#     )
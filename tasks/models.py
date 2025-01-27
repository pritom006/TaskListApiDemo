from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('lead', 'Lead'),
        ('developer', 'Developer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.username

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    is_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    developer = models.ForeignKey('User', on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.is_done and not self.completed_at:
            self.completed_at = now()
        elif not self.is_done:
            self.completed_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

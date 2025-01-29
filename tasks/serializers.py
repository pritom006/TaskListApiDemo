from rest_framework import serializers
from django.utils.timezone import localtime
from .models import Task
from django.contrib.auth import get_user_model



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user

class TaskSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()
    developer_username = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return localtime(obj.created_at).strftime('%Y-%m-%d %H:%M:%S')

    def get_updated_at(self, obj):
        return localtime(obj.updated_at).strftime('%Y-%m-%d %H:%M:%S')

    def get_completed_at(self, obj):
        if obj.completed_at:
            return localtime(obj.completed_at).strftime('%Y-%m-%d %H:%M:%S')
        return None
    
    def get_developer_username(self, obj):  
        if obj.developer:
            return obj.developer.username
        return None

    class Meta:
        model = Task
        fields = '__all__'
from django.contrib import admin
from .models import Task, User

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_done', 'created_at', 'updated_at', 'completed_at')
    list_filter = ('is_done', 'created_at', 'updated_at')  
    search_fields = ('title', 'description') 
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

admin.site.register(User)

from django.shortcuts import render
from rest_framework.response import Response
from django.views import View





def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def tasks_view(request):
    return render(request, 'tasks.html')

def task_detail_view(request):
    return render(request, 'task_detail.html')









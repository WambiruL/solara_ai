from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from .models import UserProfile
from chatbot.views import chatbot

# Create your views here.
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                auth.login(request, user)
                return redirect('login')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html')
        else:
            error_message = 'Passwords don\'t match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username = username, password = password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid Username or Password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
    
def logout(request):
    auth.logout(request)
    return redirect('')
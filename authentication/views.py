from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from .models import UserProfile

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
                return redirect('')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html')
        else:
            error_message = 'Passwords don\'t match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html', {'error_message':error_message})

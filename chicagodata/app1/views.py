from django.shortcuts import render, HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
# Create your views here.
@never_cache
@login_required(login_url='signuplogin')
def HomePage(request):
    return render (request,'home.html')

def SignupLogin(request):
    if request.method == 'POST':
        if 'form1_submit' in request.POST:
            uname = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('pass1')
            password1= request.POST.get('pass3')
            if password != password1:
                return HttpResponse("Your Passwords does not match")
            else:
                my_user= User.objects.create_user(uname,email,password)
                my_user.save()
                return redirect('signuplogin')
        if 'form2_submit' in request.POST:
            username = request.POST.get('username1')
            password2 = request.POST.get('pass2')
            print(username,password2)
            user = authenticate(request, username=username, password=password2)
            if user is not None:
                print(user)
                print("Inside user")
                login(request,user)
                return redirect('home')
            else:
                return HttpResponse("email or password is incorrect!")
            # print(email, password)
    return render (request,'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('signuplogin')
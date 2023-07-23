from django.shortcuts import render, HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
import requests
from datetime import datetime
# Create your views here.
def get_crime_data(latitude, longitude, miles):
    url = "https://data.cityofchicago.org/resource/crimes.json"
    params = {
        "$where": f"within_circle(location, {latitude}, {longitude}, {miles} )",  # 2 miles in meters
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

def get_top_five_crimes(data):
    crime_counts = {}
    for record in data:
        crime_type = record["primary_type"]
        if crime_type not in crime_counts:
            crime_counts[crime_type] = 0
        crime_counts[crime_type] += 1

    top_five_crimes = sorted(crime_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return top_five_crimes

def get_miles(mile):
    return mile * 1609.34

def get_day_of_week_counts(data):
    day_of_week_counts = {}
    for record in data:
        date_str = record["date"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")  # Updated date format to include milliseconds
        day_of_week = date_obj.weekday()

        if day_of_week not in day_of_week_counts:
            day_of_week_counts[day_of_week] = 0
        day_of_week_counts[day_of_week] += 1

    return day_of_week_counts

@never_cache
@login_required(login_url='signuplogin')
def HomePage(request):
    if request.method == 'POST':
        latitude = float(request.POST.get('lat'))
        longitude = float(request.POST.get('lon'))
        radius = int(request.POST.get('rad'))
        miles = get_miles(radius)
        print(latitude,longitude,miles)

        data = get_crime_data(latitude, longitude, miles)

        if data is not None:
            top_five_crimes = get_top_five_crimes(data)

            # Prepare the data for each chart
            bar_chart_data = {
                "labels": [crime_type for crime_type, _ in top_five_crimes],
                "data": [count for _, count in top_five_crimes],
            }

            pie_chart_data = {
                "labels": [crime_type for crime_type, _ in top_five_crimes],
                "data": [count for _, count in top_five_crimes],
            }

            line_chart_data = {
                "labels": [crime_type for crime_type, _ in top_five_crimes],
                "data": [count for _, count in top_five_crimes],
            }

            day_of_week_counts = get_day_of_week_counts(data)

    # Prepare the data for each day of the week chart
            bar_chart_data_day = {
                "labels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "data": [day_of_week_counts.get(i, 0) for i in range(7)],
            }

            pie_chart_data_day = {
                "labels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "data": [day_of_week_counts.get(i, 0) for i in range(7)],
            }

            line_chart_data_day = {
                "labels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "data": [day_of_week_counts.get(i, 0) for i in range(7)],
            }

            # Return the chart data in JSON format
            return JsonResponse({
                "bar_chart_data": bar_chart_data,
                "pie_chart_data": pie_chart_data,
                "line_chart_data": line_chart_data,
                "bar_chart_data_day": bar_chart_data_day,
                "pie_chart_data_day": pie_chart_data_day,
                "line_chart_data_day": line_chart_data_day,
            })

    # return JsonResponse({"error": "Invalid request"}, status=400)
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
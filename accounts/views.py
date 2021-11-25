from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    )
from . models import User
def registration(request):
	template_name = "registration.html"
	if request.method == "POST":
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		phone_number = request.POST.get('phone_number')
		email = request.POST.get('email')
		password = request.POST.get('password')
		confirm_password = request.POST.get('confirm_password')

		user = User(
			email=email, 
			first_name=first_name, 
			last_name=last_name,
			phone_number=phone_number,
			)

		user.set_password(password)
		user.save()
		
		userIn = authenticate(email=email, password=password)
		if userIn:
			login(request, userIn)
			next_endpoint = request.GET.get("next", '')
			return redirect("/")
	return render(request, template_name)

def login_user(request):
	template_name = "login.html"

	if request.method == "POST":
		email = request.POST.get('email')
		password = request.POST.get('password')

		userIn = authenticate(email=email, password=password)
		if userIn:
			login(request, userIn)
			next_endpoint = request.GET.get("next", '')
			return redirect("/")
	return render(request, template_name)


def logout_user(request):
	logout(request)
	return redirect("accounts:login")


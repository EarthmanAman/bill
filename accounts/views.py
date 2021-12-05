from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    )
from django.contrib import messages

from . models import User
def registration(request):
	template_name = "registration.html"
	error = False
	if request.method == "POST":
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		phone_number = request.POST.get('phone_number')
		email = request.POST.get('email')
		password = request.POST.get('password')
		confirm_password = request.POST.get('confirm_password')

		user_in = User.objects.filter(email=email)
		if user_in.exists():
			messages.add_message(request, messages.ERROR, 'User with this email already exists. Please login')
			return render(request, template_name)

		if password != confirm_password:
			messages.add_message(request, messages.ERROR, 'Password Do not Match')
			error = True
		if len(str(phone_number)) != 9:
			messages.add_message(request, messages.ERROR, 'Phone number is invalid')
			error = True
		if not error:
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


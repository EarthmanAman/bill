from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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


@login_required
def logout_user(request):
	logout(request)
	return redirect("accounts:login")

@login_required
def update(request, user_id):
	user = get_object_or_404(User, pk=user_id)

	if request.method == "POST":
		first_name = request.POST.get("first_name", user.first_name)
		last_name = request.POST.get("last_name", user.last_name)
		email = request.POST.get("email", user.email)
		phone_number = request.POST.get("phone_number", user.phone_number)

		email_change = user.email != email

		user.first_name = first_name
		user.last_name = last_name
		user.email = email
		try:
			user.phone_number = int(phone_number)
		except:
			None
		user.save()

		if email_change:
			messages.add_message(request, messages.SUCCESS, 'You updated your email you must log in again.')
			return redirect("accounts:login")
	return redirect("main:profile")

@login_required
def update_password(request):
	if request.method == "POST":
		old_pass = request.POST.get("old_password")
		new_pass = request.POST.get("new_password")
		confirm_new_pass = request.POST.get("confirm_new_password")

		userIn = authenticate(email=request.user.email, password=old_pass)
		if userIn:
			if new_pass == confirm_new_pass:
				user = request.user
				user.set_password(new_pass)
				user.save()
				messages.add_message(request, messages.SUCCESS, 'You updated your password you must log in again.')
				return redirect("accounts:login")
			else:
				messages.add_message(request, messages.ERROR, 'Password do not match')
				return redirect("main:profile")
		else:
			messages.add_message(request, messages.ERROR, 'Old Password is wrong!')
			return redirect("main:profile")
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    )
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count
from django.conf import settings
from django.core.mail import send_mail

from . models import User, Message
from main.models import Subscription
from mpesa_api.models import MpesaPayment

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

		# Check if there is a user with the given email
		user_in = User.objects.filter(email=email)
		if user_in.exists():
			messages.add_message(request, messages.ERROR, 'User with this email already exists. Please login')
			return render(request, template_name)

		# Confirm password
		if password != confirm_password:
			messages.add_message(request, messages.ERROR, 'Password Do not Match')
			error = True
		else:
			SpecialSym=['$','@','#', "!", "$", "%", "^", "&", "*", ".", "(", ")"]
			return_val = True
			if len(password) < 6:
				messages.add_message(request, messages.ERROR, 'The length of password should be at least 6 char long')
				return_val=False
			if not any(char.isdigit() for char in password):
				messages.add_message(request, messages.ERROR, 'The password should have at least one numeral')
				return_val=False
			if not any(char.isupper() for char in password):
				messages.add_message(request, messages.ERROR, 'The password should have at least one uppercase letter')
				return_val=False
			if not any(char.islower() for char in password):
				messages.add_message(request, messages.ERROR, 'The password should have at least one lowercase letter')
				return_val=False
			if not any(char in SpecialSym for char in password):
				messages.add_message(request, messages.ERROR, 'The password should have at least one special character')
				return_val = False

			if return_val == False:
				return render(request, template_name)
		# Check phone number
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
			if request.user.is_superuser == True:
				return redirect("accounts:admin_index")
			next_endpoint = request.GET.get("next", '')
			return redirect("/")
		else:
			messages.add_message(request, messages.ERROR, 'The user with given crediatials does not exists.')
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

@login_required
def create_message(request):
	if request.method == "POST":
		subject = request.POST.get("subject")
		message = request.POST.get("message")

		if message != None:
			message = Message.objects.create(user=request.user, subject=subject, message=message)
	messages.add_message(request, messages.SUCCESS, 'Message sent successful')
	return redirect("main:index") 

def subscription_total():
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	subscriptions = []
	for subscription in Subscription.objects.all():
		subscriptions.append({"name": subscription.name, "months":[], "transactions":0})
		mpesa = MpesaPayment.objects.filter(my_subscription__subscription=subscription)

		months_total = mpesa.filter(created_at__year='2021').values_list('created_at__month').annotate(total_item=Sum('amount'), total_count=Count('id'))
		for idx, month in enumerate(months_total):
			subscriptions[-1]["months"].append({
				"month":months[month[0]-1],
				"month_no":month[0]-1, 
				"amount":month[1], 
				"transactions":month[2], 
				"no":idx+1,
				"revenue": float(month[1]) * 0.05,
			})
			
	return subscriptions

def month_total(start, last):
	mpesa = MpesaPayment.objects.filter(created_at__gte=start).filter(created_at__lte=last)
	trans = mpesa.values_list('my_subscription__subscription__name').annotate( total_amount=Sum('amount'))
	subscriptions = []
	total = 0
	for idx, tran in enumerate(trans):
		m = mpesa.filter(my_subscription__subscription__name=tran[0])
		subscriptions.append({"name":tran[0], "amount":tran[1], "commission":round(float(tran[1])*0.05, 2), "index":idx+1, "trans":len(m)})
		total += round(float(tran[1])*0.05, 2)

	return subscriptions, total

def create_m():
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	m = []
	for n in months:
		m.append({"name":n, "index":months.index(n)+1})
	return m

@login_required
def admin_index(request):
	template_name = "./admin_index.html"
	subscriptions = subscription_total()
	
	if request.user.is_superuser:

		month  = request.GET.get("month", None)
		first  = request.GET.get("start", None)
		last  = request.GET.get("last", None)
		total = 0
		if first and last:
			print("in heree")
			months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
			subscriptions, total = month_total(first, last)
			
			context = {
				"start":first,
				"last": last,
				"subscriptions": subscriptions,
				"total": total,
				"nbar": "stats"
			}

			return render(request, "./report.html", context)
		context = {
			"nbar": "stats",
			"months": create_m(),
			"subscriptions": subscriptions,
		}
		return render(request, template_name, context)
	else:
		redirect("main:index")

@login_required
def admin_messages(request):
	template_name = "./admin_messages.html"
	messages = Message.objects.all().order_by("-pk")
	message_id = request.GET.get("message_id")
	message = None

	if message_id:
		message = messages.get(pk=int(message_id))
		message.read = True
		message.save()

	if request.user.is_superuser:
		context = {
			"nbar": "messages",
			"messages": messages,
			"message": message,
		}
		return render(request, template_name, context)
	else:
		redirect("main:index")

def forget_password(request):
	if request.method == "POST":
		email = request.POST.get("email")
		user = User.objects.filter(email=email)
		if user.exists():
			user = user.last()
			subject = 'FORGOT PASSWORD'
			password = gen_pass()
			msg = f'Hi {user.first_name} {user.last_name}, \n\nYou are receiving this email because you requested a password reset.\n\nUse below password then make sure you go and update it for security reasons. \n\n\nPassword:  {password}'
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, msg, email_from, recipient_list)
			user.set_password(password)
			user.save()
		messages.add_message(request, messages.SUCCESS, 'Check your email')

	return render(request, "./forgot_password.html")



import random
import array
 
def gen_pass():
	# maximum length of password needed
	# this can be changed to suit your password length
	MAX_LEN = 8
	  
	# declare arrays of the character that we need in out password
	# Represented as chars to enable easy string concatenation
	DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']  
	LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 
	                     'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
	                     'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
	                     'z']
	  
	UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 
	                     'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
	                     'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
	                     'Z']
	  
	SYMBOLS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>', 
	           '*', '(', ')', '<']
	  
	# combines all the character arrays above to form one array
	COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS + SYMBOLS
	  
	# randomly select at least one character from each character set above
	rand_digit = random.choice(DIGITS)
	rand_upper = random.choice(UPCASE_CHARACTERS)
	rand_lower = random.choice(LOCASE_CHARACTERS)
	rand_symbol = random.choice(SYMBOLS)
	  
	# combine the character randomly selected above
	# at this stage, the password contains only 4 characters but 
	# we want a 12-character password
	temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol
	  
	  
	# now that we are sure we have at least one character from each
	# set of characters, we fill the rest of
	# the password length by selecting randomly from the combined 
	# list of character above.
	for x in range(MAX_LEN - 4):
		temp_pass = temp_pass + random.choice(COMBINED_LIST)

		# convert temporary password into array and shuffle to 
		# prevent it from having a consistent pattern
		# where the beginning of the password is predictable
		temp_pass_list = array.array('u', temp_pass)
		random.shuffle(temp_pass_list)
	  
	# traverse the temporary password array and append the chars
	# to form the password
	password = ""
	for x in temp_pass_list:
		password = password + x
	          
	# print out password
	return password
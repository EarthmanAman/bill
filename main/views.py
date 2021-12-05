from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . models import Subscription, MySubscription, Bill


def get_pending_bills(request):
	pendings = []
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	for bill in Bill.objects.filter(my_subscription__user=request.user).order_by("-pk"):
		if bill.credit > bill.debit and bill.for_date <= date.today():
			pendings.append({
					"id": bill.id, 
					"my_subscription": bill.my_subscription,
					"month":months[bill.for_date.month - 1], 
					"amount": bill.credit, 
					"payable": bill.credit - bill.debit
				})

	return pendings

def get_upcoming_bills(request):
	upcoming = []
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	for bill in Bill.objects.filter(my_subscription__user=request.user).order_by("-pk"):
		if bill.for_date > date.today():
			upcoming.append({
					"id": bill.id, 
					"my_subscription": bill.my_subscription,
					"month":months[bill.for_date.month - 1], 
					"amount": bill.credit, 
					"payable": bill.credit - bill.debit
				})

	return upcoming

@login_required
def index(request):
	template_name = "index.html"
	subscriptions = Subscription.objects.all()
	my_subscriptions = MySubscription.objects.all()
	pending_bills = get_pending_bills(request)
	upcoming_bills = get_upcoming_bills(request)
	context = {
		"nbar":"home",
		"subscriptions":subscriptions,
		"my_subscriptions":my_subscriptions,
		"pending_bills": pending_bills,
		"upcoming_bills": upcoming_bills,
	}
	return render(request, template_name, context)

def register_subscription(request):
	if request.method == "POST":
		subscription = request.POST.get("subscription")
		account = request.POST.get("account")
		subscription = Subscription.objects.get(pk=int(subscription))
		my_subscription = MySubscription.objects.create(user=request.user, subscription=subscription, account_no=account)

	return redirect("main:index")

@login_required
def invoices(request):
	template_name = "invoices.html"
	context = {
		"nbar":"invoices"
	}
	return render(request, template_name, context)

@login_required
def profile(request):
	template_name = "profile.html"
	context = {
		"nbar":"profile",
		"user": request.user,
	}
	return render(request, template_name, context)


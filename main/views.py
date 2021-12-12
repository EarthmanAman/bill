import csv
from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from . models import Subscription, MySubscription, Bill, Package, Channel
from django.views.generic import View
from django.template.loader import get_template
from . utils import render_to_pdf #created in step 4
from django.contrib import messages
from mpesa_api.models import MpesaPayment
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

def get_bills(bills_list):
	bills = []
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	for bill in bills_list:
		
		bills.append({
				"id": bill.id, 
				"my_subscription": bill.my_subscription,
				"month":months[bill.for_date.month - 1], 
				"amount": bill.credit, 
				"payable": bill.credit - bill.debit,
				"paid": True if bill.credit - bill.debit == 0  else False,
			})

	return bills

@login_required
def index(request):
	if request.user.is_superuser == True:
		return redirect("admin:index")
	template_name = "index.html"
	subscriptions = Subscription.objects.all()
	my_subscriptions = MySubscription.objects.filter(user=request.user)
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

def simulate(subscription, account):
	filename = "main/kplc_bill.csv"
	if subscription.subscription.name.upper() == "WATER":
		filename = "main/water_bill.csv"
	elif subscription.subscription.name.upper() == "DSTV":
		filename = "main/dstv_bill.csv"

	with open(filename, 'r') as file:
		reader = csv.reader(file)
		headers = next(reader)

		for contents in reader:
			print(account)
			print(contents[0])
			print("*"*50)
			if contents[0] == str(account):
				m = contents[1][0:2]
				d = contents[1][3:5]
				y = contents[1][6:]
				date = datetime.strptime(y + "-" + m + "-" + d, "%Y-%m-%d").date()
				
				bill = Bill.objects.create(my_subscription=subscription, for_date=date, credit=float(contents[2]), debit=float(contents[3]), units=contents[4])
				if float(contents[3]) <= float(contents[3]):
					mpesa = MpesaPayment.objects.create(my_subscription=subscription, amount=float(contents[2]))

@login_required
def register_subscription(request):
	if request.method == "POST":
		subscription = request.POST.get("subscription")
		account = request.POST.get("account")
		subscription = Subscription.objects.get(pk=int(subscription))
		if subscription in [subs.subscription for subs in request.user.mysubscription_set.all()]:
			messages.add_message(request, messages.WARNING, 'You already subscribed to this!')
		else:
			my_subscription = MySubscription.objects.create(user=request.user, subscription=subscription, account_no=account)
			simulate(my_subscription, account)

	return redirect("main:index")

def create_months_dict(bills):
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	l = {}
	ls = []
	months.reverse()
	for month in months:
		l[(2021, month)] = {"title": month, "bills":[]}

	for idx, bill in enumerate(bills):
		m = 12 - bill.for_date.month 
		month = months[m]
		if bill.credit - bill.debit <= 0:
			l[(2021, month)]["bills"].append({"bill":bill, "paid": True, "no":len(l[(2021, month)]["bills"]) + 1})
		else:
			l[(2021, month)]["bills"].append({"bill":bill, "status":False, "no":len(l[(2021, month)]["bills"]) + 1})
	for key in list(l.keys()):
		ls.append(l[key])
	return ls
@login_required
def invoices(request):
	if request.user.is_superuser == True:
		return redirect("admin:index")
	template_name = "invoices.html"
	invoices_list = Bill.objects.all()
	i = create_months_dict(invoices_list)

	query = request.GET.get("query")
	if query:
		i = list(filter(lambda bill: query.lower() in bill["title"].lower(), i))
	context = {
		"nbar":"invoices",
		"invoices":i,
		"query": query,
	}
	return render(request, template_name, context)


@login_required
def invoice(request, bill_id):
	if request.user.is_superuser == True:
		return redirect("admin:index")
	template_name = "invoice.html"
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	bill = get_object_or_404(Bill, pk=bill_id)
	paid = False
	
	if bill.credit <= bill.debit:
		paid = True
	
	bill_dict = {
		"id": bill.id,
		"bill":bill,
		"month": months[bill.for_date.month - 1],
		"balance": bill.credit,
		"payable": bill.credit - bill.debit,
		"amount": bill.debit,
		"date": bill.for_date,
	}
	context = {
		"nbar":"invoices",
		"bill":bill_dict,
		"paid":paid,
	}

	download = request.GET.get("download")
	if download:
		template = get_template("invoice_download.html")
		html = template.render(context)
		pdf = render_to_pdf('invoice_download.html', context)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = "Invoice_%s.pdf" %(str(bill.id))
			#content = "inline; filename='%s'" %(filename)
			content = "attachment; filename='%s'" %(filename)
			response['Content-Disposition'] = content
			return response

	return render(request, template_name, context)



@login_required
def profile(request):
	if request.user.is_superuser == True:
		return redirect("admin:index")
	template_name = "profile.html"
	trans = MpesaPayment.objects.filter(my_subscription__user=request.user).order_by("-pk")
	context = {
		"nbar":"profile",
		"user": request.user,
		"trans":trans,
	}
	return render(request, template_name, context)


@login_required

def delete_bill(request, bill_id):
	bill = Bill.objects.get(pk=bill_id)
	bill.delete()
	return redirect("main:index")


def get_unit(subscription):
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	packages = subscription.subscription.package_set.all()
	if len(packages) > 0:
		package = Bill.objects.filter(my_subscription=subscription)[0]
		package = Package.objects.filter(name=package.units)[0]
		channels = package.channel_set.all()
		return True, channels

	units = []
	for bill in subscription.bill_set.all():
		units.append({"month":months[bill.for_date.month-1], "units":bill.units})
	return False, units

@login_required
def subscription(request, subscription_id):
	if request.user.is_superuser == True:
		return redirect("admin:index")
	template_name = "other_subscriptions.html"
	subscription = get_object_or_404(MySubscription, pk=subscription_id)
	trans = MpesaPayment.objects.filter(my_subscription=subscription).order_by("-pk")
	bills = get_bills(subscription.bill_set.all().order_by("pk"))
	units = get_unit(subscription)
	context = {
		"nbar":"home",
		"subscription": subscription,
		"bills":bills,
		"trans":trans[:4],
		"channel": units[0],
		"units":units[1],
	}
	return render(request, template_name, context)

def delete_subscription(request, subscription_id):
	sub = MySubscription.objects.get(pk=subscription_id)
	sub.delete()
	messages.add_message(request, messages.SUCCESS, 'Deleted Successfully')
	return redirect("main:index")


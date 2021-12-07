from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from . models import Subscription, MySubscription, Bill
from django.views.generic import View
from django.template.loader import get_template
from . utils import render_to_pdf #created in step 4
from django.contrib import messages

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
				"payable": bill.credit - bill.debit
			})

	return bills

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
		if subscription in [subs.subscription for subs in request.user.mysubscription_set.all()]:
			messages.add_message(request, messages.WARNING, 'You already subscribed to this!')
		else:
			my_subscription = MySubscription.objects.create(user=request.user, subscription=subscription, account_no=account)

	return redirect("main:index")

def create_months_dict(bills):
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	l = {}
	ls = []
	months.reverse()
	for month in months:
		l[(2021, month)] = {"title": month, "bills":[]}

	for bill in bills:
		m = 12 - bill.for_date.month 
		month = months[m]
		if bill.credit - bill.debit <= 0:
			l[(2021, month)]["bills"].append({"bill":bill, "paid": True})
		else:
			l[(2021, month)]["bills"].append({"bill":bill, "status":False})
	for key in list(l.keys()):
		ls.append(l[key])
	return ls
@login_required
def invoices(request):
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
	template_name = "profile.html"
	context = {
		"nbar":"profile",
		"user": request.user,
	}
	return render(request, template_name, context)


@login_required

def delete_bill(request, bill_id):
	bill = Bill.objects.get(pk=bill_id)
	bill.delete()
	return redirect("main:index")


@login_required
def subscription(request, subscription_id):
	template_name = "other_subscriptions.html"
	subscription = get_object_or_404(MySubscription, pk=subscription_id)
	bills = get_bills(subscription.bill_set.all())
	context = {
		"nbar":"home",
		"subscription": subscription,
		"bills":bills,
	}
	return render(request, template_name, context)

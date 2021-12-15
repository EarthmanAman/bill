from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from requests.auth import HTTPBasicAuth
import json
from . mpesa_credential import MpesaAccessToken, LipanaMpesaPpassword
from django.urls import reverse
from .models import MpesaPayment
from main.models import Bill, MySubscription
from django_daraja.mpesa.core import MpesaClient
from django.contrib import messages
from django.utils import timezone
import csv


def index(request, subscription_id):
	# Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
	sub = get_object_or_404(MySubscription, pk=subscription_id)
	transaction = request.POST.get("transaction")
	with open("./mpesa_api/transactions.csv", 'r') as file:
		reader = csv.reader(file)

		for contents in reader:
			if contents[0] == transaction:
				amount = float(contents[1])
				trns = MpesaPayment.objects.create(my_subscription=sub, amount=amount, created_at=timezone.now())
				for bill in sub.bill_set.all():
					if bill.credit > bill.debit:
						payable = bill.credit - bill.debit
						if amount >= payable:
							bill.debit = bill.credit
							bill.save()
							amount = amount -payable
						else:
							bill.debit = bill.debit + amount
							amount = 0
							bill.save()
				if amount > 0:
					s = sub.bill_set.first()
					s.debit = s.debit + amount
					s.save()

	
				messages.add_message(request, messages.SUCCESS, 'Payment was successful')


	nex = request.POST.get('next', "/")
	if nex == "subs":
		return redirect("main:subscription", subscription_id=subscription_id)
	elif nex == "invoice":
		return redirect("main:subscription", subscription_id=subscription_id)
	return redirect(nex)

def stk_push_callback(request):
	data = request.body
	# You can do whatever you want with the notification received from MPESA here.
	print("in call back")
	print(data)
	

def lipa_na_mpesa_online(request):
	access_token = MpesaAccessToken.validated_mpesa_access_token
	api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
	headers = {"Authorization": "Bearer %s" % access_token}
	request = {
	    "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
	    "Password": LipanaMpesaPpassword.decode_password,
	    "Timestamp": LipanaMpesaPpassword.lipa_time,
	    "TransactionType": "CustomerPayBillOnline",
	    "Amount": 1,
	    "PartyA": 254701467872,  # replace with your phone number to get stk push
	    "PartyB": LipanaMpesaPpassword.Business_short_code,
	    "PhoneNumber": 254701467872,  # replace with your phone number to get stk push
	    "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
	    "AccountReference": "Henry",
	    "TransactionDesc": "Testing stk push"
	}
	response = requests.post(api_url, json=request, headers=headers)
	return HttpResponse('success')


def getAccessToken(request):
	consumer_key = 'iC4LxuonW411uOyOqPZkDGtGFytD11lI'
	consumer_secret = 'VHLOEC12ekGGlYmh'
	api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
	r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
	mpesa_access_token = json.loads(r.text)
	validated_mpesa_access_token = mpesa_access_token['access_token']
	print(validated_mpesa_access_token)
	return HttpResponse(validated_mpesa_access_token)

@csrf_exempt
def register_urls(request):
	access_token = MpesaAccessToken.validated_mpesa_access_token
	api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
	headers = { 'Content-Type': 'application/json', "Authorization": "Bearer %s" % access_token}
	payload = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
	           "ResponseType": "Completed",
	           "ConfirmationURL": "https://billmanagementproject.herokuapp.com/api/v1/c2b/confirmation",
	           "ValidationURL": "hthttps://billmanagementproject.herokuapp.com/api/v1/c2b/validation",
	           }
	response = requests.request("POST", api_url, headers = headers, data = payload)
	response = response.text.encode('utf8')
	return HttpResponse(response)

#"ConfirmationURL": "https://billmanagementproject.herokuapp.com/mpesa_api/c2b/confirmation",
#"ValidationURL": "https://billmanagementproject.herokuapp.com/mpesa_api/c2b/validation"

@csrf_exempt
def call_back(request):
	pass


@csrf_exempt
def validation(request):
	context = {
	    "ResultCode": 0,
	    "ResultDesc": "Accepted"
	}
	return JsonResponse(dict(context))


@csrf_exempt
def confirmation(request):
	mpesa_body =request.body.decode('utf-8')
	mpesa_payment = json.loads(mpesa_body)
	payment = MpesaPayment(
	    first_name=mpesa_payment['FirstName'],
	    last_name=mpesa_payment['LastName'],
	    middle_name=mpesa_payment['MiddleName'],
	    description=mpesa_payment['TransID'],
	    phone_number=mpesa_payment['MSISDN'],
	    amount=mpesa_payment['TransAmount'],
	    reference=mpesa_payment['BillRefNumber'],
	    organization_balance=mpesa_payment['OrgAccountBalance'],
	    type=mpesa_payment['TransactionType'],
	)
	payment.save()
	context = {
	    "ResultCode": 0,
	    "ResultDesc": "Accepted"
	}
	return JsonResponse(dict(context))
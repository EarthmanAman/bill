from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from requests.auth import HTTPBasicAuth
import json
from . mpesa_credential import MpesaAccessToken, LipanaMpesaPpassword

from .models import MpesaPayment

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
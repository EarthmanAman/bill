
from django.contrib import admin
from django.urls import path
from . views import (
	index, 
	invoices, 
	profile,
	register_subscription,

	delete_bill,
	invoice,
	subscription,
	
)

app_name = "main"

urlpatterns = [
    path('', index, name="index"),
  
    path('invoices/', invoices, name="invoices"),
    path('profile/', profile, name="profile"),

    path('register_subscription/', register_subscription, name="register_subscription"),

    path('delete_bill/<int:bill_id>', delete_bill, name="delete_bill"),
    path('invoice/<int:bill_id>', invoice, name="invoice"),
    path('subscription/<int:subscription_id>', subscription, name="subscription"),
]

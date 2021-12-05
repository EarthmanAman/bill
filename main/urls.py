
from django.contrib import admin
from django.urls import path
from . views import (
	index, 
	invoices, 
	profile,
	register_subscription,
)

app_name = "main"

urlpatterns = [
    path('', index, name="index"),
    path('invoices/', invoices, name="invoices"),
    path('profile/', profile, name="profile"),

    path('register_subscription/', register_subscription, name="register_subscription"),
]


from django.contrib import admin
from django.urls import path
from . views import index, invoices, profile

app_name = "main"

urlpatterns = [
    path('', index, name="index"),
    path('invoices/', invoices, name="invoices"),
    path('profile/', profile, name="profile"),
]

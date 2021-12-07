
from django.contrib import admin
from django.urls import path
from . views import (
	lipa_na_mpesa_online,
	getAccessToken,
	register_urls,
	confirmation,
	validation,
	call_back,
)

app_name = "mpesa_api"

urlpatterns = [
    path('access_token', getAccessToken, name="access_token"),
    path('online/lipa', lipa_na_mpesa_online, name='lipa_na_mpesa'),

    # register, confirmation, validation and callback urls
    path('c2b/register', register_urls, name="register_mpesa_validation"),
    path('c2b/confirmation', confirmation, name="confirmation"),
    path('c2b/validation', validation, name="validation"),
    path('c2b/callback', call_back, name="call_back"),
]

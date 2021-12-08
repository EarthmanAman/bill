
from django.contrib import admin
from django.urls import path
from . views import (
	lipa_na_mpesa_online,
	getAccessToken,
	register_urls,
	confirmation,
	validation,
	call_back,

	index,
	stk_push_callback,
)

app_name = "mpesa_api"

urlpatterns = [
    path('access_token', getAccessToken, name="access_token"),
    path('online/lipa/<int:bill_id>', index, name='lipa_na_mpesa'),
    path('daraja/stk-push', stk_push_callback, name='mpesa_stk_push_callback'),
    # register, confirmation, validation and callback urls
    path('c2b/register', register_urls, name="register_mpesa_validation"),
    path('c2b/confirmation', confirmation, name="confirmation"),
    path('c2b/validation', validation, name="validation"),
    path('c2b/callback', call_back, name="call_back"),
]

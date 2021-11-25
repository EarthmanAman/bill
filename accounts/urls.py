
from django.contrib import admin
from django.urls import path
from . views import (
	registration, 
	login_user,
	logout_user,
)

app_name = "accounts"

urlpatterns = [
    path('registration', registration, name="registration"),
    path('login/', login_user, name="login"),
    path('logout/', logout_user, name="logout"),
]


from django.contrib import admin
from django.urls import path
from . views import (
	registration, 
	login_user,
	logout_user,
	update,
	update_password,
	create_message,
	admin_index,
	admin_messages,
	forget_password,
)

app_name = "accounts"

urlpatterns = [
    path('registration', registration, name="registration"),
    path('login/', login_user, name="login"),
    path('logout/', logout_user, name="logout"),
    path('update/<int:user_id>', update, name="update"),
    path('update_password', update_password, name="update_password"),
    path('create_message', create_message, name="create_message"),
    path('admin_index', admin_index, name="admin_index"),
    path('admin_messages', admin_messages, name="admin_messages"),
    path('forget_password', forget_password, name="forget_password"),
]

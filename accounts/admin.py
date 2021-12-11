from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import TextInput, Textarea

from . models import User, Message


class UserAdminConfig(UserAdmin):
	search_fields = ("email",)
	list_filter = ("is_active", "is_staff")
	ordering = ("-start_date",)
	list_display = ("email",  "first_name", "last_name", "is_active", "is_staff")

	fieldsets = (
		(None, {"fields":("email", "avatar", "password",  "first_name", "last_name", "phone_number")}),
		("Permissions", {"fields":("is_staff", "is_active", "groups", "user_permissions")}),
	)

	add_fieldsets = (
		(None, {
			"classes": ("wide",),
			"fields": ("email", "first_name", "last_name", "avatar", "phone_number", "password1", "password2"),
			}
		),
		("Permissions", {
			"classes": ("wide",),
			"fields": ("is_staff", "groups", "user_permissions"),
			}
		),
	)
admin.site.register(User, UserAdminConfig)
admin.site.register(Message)

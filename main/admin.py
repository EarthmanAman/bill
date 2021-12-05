from django.contrib import admin

from . models import (
	Subscription,
	MySubscription,
	Bill,
)

admin.site.register(Subscription)
admin.site.register(MySubscription)
admin.site.register(Bill)
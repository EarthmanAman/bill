from django.contrib import admin

from . models import (
	Subscription,
	MySubscription,
	Bill,
	Package,
	Channel,
)

admin.site.register(Subscription)
admin.site.register(MySubscription)
admin.site.register(Bill)
admin.site.register(Package)
admin.site.register(Channel)
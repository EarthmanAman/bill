from django.db import models
from main.models import MySubscription

class BaseModel(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


# M-pesa Payment models

class MpesaCalls(BaseModel):
	ip_address = models.TextField()
	caller = models.TextField()
	conversation_id = models.TextField()
	content = models.TextField()

	class Meta:
		verbose_name = 'Mpesa Call'
		verbose_name_plural = 'Mpesa Calls'


class MpesaCallBacks(BaseModel):
	ip_address = models.TextField()
	caller = models.TextField()
	conversation_id = models.TextField()
	content = models.TextField()

	class Meta:
		verbose_name = 'Mpesa Call Back'
		verbose_name_plural = 'Mpesa Call Backs'


class MpesaPayment(BaseModel):
	my_subscription = models.ForeignKey(MySubscription, on_delete=models.CASCADE, blank=True, null=True)
	amount = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return self.first_name
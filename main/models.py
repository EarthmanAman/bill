from django.db import models

from accounts.models import User


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Subscription(models.Model):
	name 	= models.CharField(max_length=50)
	pic 	= models.ImageField(upload_to="./subscriptions")

	def __str__(self):
		return self.name
class Package(models.Model):
	subscription 	= models.ForeignKey(Subscription, on_delete=models.CASCADE)
	name 			= models.CharField(max_length=50)

	def __str__(self):
		return self.name
		
class Channel(models.Model):
	package 	= models.ForeignKey(Package, on_delete=models.CASCADE)
	channel_no	= models.IntegerField()
	name 		= models.CharField(max_length=100)

	def __str__(self):
		return self.name

class MySubscription(BaseModel):
	user 			= models.ForeignKey(User, on_delete=models.CASCADE)
	subscription 	= models.ForeignKey(Subscription, on_delete=models.CASCADE)
	account_no 		= models.CharField(max_length=100)

	def __str__(self):
		return self.user.email +" : " + self.subscription.__str__() + " : " + self.account_no

class Bill(BaseModel):
	my_subscription 	= models.ForeignKey(MySubscription, on_delete=models.CASCADE)
	for_date			= models.DateField(blank=True, null=True)
	credit 				= models.FloatField()
	debit 				= models.FloatField()
	units 				= models.CharField(max_length=50, default="0.0")

	def __str__(self):
		return str(self.for_date) + " : " + self.my_subscription.__str__() + "  => (" + str(self.credit) + " , " + str(self.debit) + ")"

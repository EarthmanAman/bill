from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
	template_name = "index.html"
	context = {
		"nbar":"home"
	}
	return render(request, template_name, context)

@login_required
def invoices(request):
	template_name = "invoices.html"
	context = {
		"nbar":"invoices"
	}
	return render(request, template_name, context)

@login_required
def profile(request):
	template_name = "profile.html"
	context = {
		"nbar":"profile",
		"user": request.user,
	}
	return render(request, template_name, context)


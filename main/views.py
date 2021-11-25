from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
	template_name = "index.html"
	return render(request, template_name)

@login_required
def invoices(request):
	template_name = "invoices.html"
	return render(request, template_name)

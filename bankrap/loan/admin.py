from django.contrib import admin
from .models import LoanRequest, LoanOffer

# Register your models here.
admin.site.register(LoanRequest)
admin.site.register(LoanOffer)

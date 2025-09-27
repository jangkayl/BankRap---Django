from django.contrib import admin
from .models import User, LenderProfile, BorrowerProfile

# Register your models here.
admin.site.register(User)
admin.site.register(LenderProfile)
admin.site.register(BorrowerProfile)

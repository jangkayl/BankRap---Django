from django.shortcuts import render
from django.views import View
from .models import User
# Create your views here.

class AccountView(View):
    template_name = 'account.html'

    def get(self,request):
        accounts = User.objects.all()
        return render(request, self.template_name, {'accounts': accounts})

class ProfileView(View):
    template_name = 'profile.html'

    def get(self, request):
        # In a real application, you would fetch the current user's data here
        # For this example, we'll just render the template
        return render(request, self.template_name)
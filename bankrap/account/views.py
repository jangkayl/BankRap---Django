from django.shortcuts import render
from django.views import View
from .models import User
# Create your views here.

class AccountView(View):
    template_name = 'account.html'

    def get(self,request):
        accounts = User.objects.all()
        return render(request, self.template_name, {'accounts': accounts})

from django.shortcuts import render
from django.views import View
# Create your views here.

class AccountView(View):
    template_name = 'account.html'

    def get(self,request):
        return render(request, self.template_name)
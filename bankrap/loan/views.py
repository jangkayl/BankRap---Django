from django.shortcuts import render
from django.views import View
from .models import LoanRequest
# Create your views here.

class LoanView(View):
    template_name = 'loan.html'

    def get(self,request):
        loans = LoanRequest.objects.all()
        return render(request, self.template_name, {'loans': loans})

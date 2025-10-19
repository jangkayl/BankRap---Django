from django.shortcuts import render
from django.views import View
# Create your views here.

class TransactionView(View):
    template_name = 'transaction.html'

    def get(self,request):
        return render(request, self.template_name)
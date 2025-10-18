from django.shortcuts import render
from django.views import View
from .models import ReviewAndRating

class ReviewView(View):
    template_name = 'review.html'

    def get(self, request):
        reviews = ReviewAndRating.objects.all()
        return render(request, self.template_name, {'reviews': reviews})

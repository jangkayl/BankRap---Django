from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import ReviewAndRating
from account.models import User

class ReviewView(View):
    template_name = 'review.html'

    def get(self, request):
        user_id = 1  # temporary logged-in user
        users = User.objects.exclude(user_id=user_id)
        reviews = ReviewAndRating.objects.all()
        return render(request, self.template_name, {
            'reviews': reviews,
            'users': users,
        })

    def post(self, request):
        user_id = 1  # temporary logged-in user
        reviewer = User.objects.get(user_id=user_id)
        reviewee_id = request.POST.get('reviewee')
        review_type = request.POST.get('review_type')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        reviewee = User.objects.get(user_id=reviewee_id)
        ReviewAndRating.objects.create(
            reviewer=reviewer,
            reviewee=reviewee,
            rating=rating,
            comment=comment,
            review_type=review_type
        )
        messages.success(request, 'Review submitted successfully!')
        return redirect('review')

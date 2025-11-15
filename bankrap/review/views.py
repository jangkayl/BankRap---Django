from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .models import ReviewAndRating
from account.models import User

class ReviewView(View):
    template_name = 'review.html'

    def get(self, request):
        # prefer the real logged-in user if available, fall back to temporary user_id=1
        if hasattr(request, "user") and request.user and request.user.is_authenticated:
            try:
                user_id = request.user.user_id
            except Exception:
                user_id = 1
        else:
            user_id = 1  # temporary logged-in user

        try:
            current_user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            # fallback to first user if user_id not present in DB
            current_user = User.objects.first()
            user_id = current_user.user_id if current_user else 1

        users = User.objects.exclude(user_id=user_id)

        # fetch reviews split into "given" and "received" relative to the current user
        # Use the model's review_date field (auto_now_add)
        given_reviews = ReviewAndRating.objects.filter(reviewer=current_user).order_by('-review_date')
        received_reviews = ReviewAndRating.objects.filter(reviewee=current_user).order_by('-review_date')

        return render(request, self.template_name, {
            'users': users,
            'current_user_id': user_id,
            'given_reviews': given_reviews,
            'received_reviews': received_reviews,
            'given_count': given_reviews.count(),
            'received_count': received_reviews.count(),
        })

    def post(self, request):
        # prefer the real logged-in user if available, fall back to temporary user_id=1
        if hasattr(request, "user") and request.user and request.user.is_authenticated:
            try:
                user_id = request.user.user_id
            except Exception:
                user_id = 1
        else:
            user_id = 1  # temporary logged-in user

        try:
            reviewer = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            messages.error(request, "Reviewer not found.")
            return redirect('review')

        # handle delete first
        if request.POST.get('delete'):
            review_id = request.POST.get('review_id')
            if not review_id:
                messages.error(request, "Missing review id.")
                return redirect('review')
            try:
                review_obj = ReviewAndRating.objects.get(pk=review_id, reviewer=reviewer)
            except ReviewAndRating.DoesNotExist:
                messages.error(request, "Review not found or you don't have permission to delete it.")
                return redirect('review')
            review_obj.delete()
            messages.success(request, "Review deleted successfully!")
            return redirect('review')

        # otherwise create or update
        review_id = request.POST.get('review_id')  # will be present for edits
        reviewee_id = request.POST.get('reviewee')
        review_type = request.POST.get('review_type')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # basic validation
        if not reviewee_id or not rating:
            messages.error(request, "Please select a reviewee and a rating.")
            return redirect('review')

        try:
            reviewee = User.objects.get(user_id=reviewee_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user does not exist.")
            return redirect('review')

        # If review_id present -> update existing review (only if current user is the reviewer)
        if review_id:
            try:
                # use pk lookup (works regardless of the field name used for the primary key)
                review_obj = ReviewAndRating.objects.get(pk=review_id, reviewer=reviewer)
            except ReviewAndRating.DoesNotExist:
                messages.error(request, "Review not found or you don't have permission to edit it.")
                return redirect('review')

            # update fields
            review_obj.reviewee = reviewee
            review_obj.rating = int(rating)
            review_obj.comment = comment or ''
            review_obj.review_type = review_type
            review_obj.save()
            messages.success(request, "Review updated successfully!")
            return redirect('review')

        # Otherwise create a new review
        ReviewAndRating.objects.create(
            reviewer=reviewer,
            reviewee=reviewee,
            rating=int(rating),
            comment=comment or '',
            review_type=review_type
        )
        messages.success(request, "Review submitted successfully!")
        return redirect('review')

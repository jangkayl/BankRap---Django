from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from account.models import User
from loan.models import LoanRequest
from .models import ReviewAndRating


def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None
    return None


def reviews_view(request):
    user = get_current_user(request)
    if not user: return redirect('login')

    # Fetch Reviews
    active_tab = request.GET.get('tab', 'received')
    reviews = []

    if active_tab == 'received':
        reviews = ReviewAndRating.objects.filter(reviewee=user).order_by('-review_date')
    else:
        reviews = ReviewAndRating.objects.filter(reviewer=user).order_by('-review_date')

    # Calculate Trust Score
    received_all = ReviewAndRating.objects.filter(reviewee=user)
    avg_rating = 0
    if received_all.exists():
        avg_rating = sum([r.rating for r in received_all]) / received_all.count()

    return render(request, 'review/ratings.html', {
        'user': user,
        'reviews': reviews,
        'active_tab': active_tab,
        'avg_rating': round(avg_rating, 1),
        'review_count': received_all.count()
    })


def create_review(request, loan_id):
    user = get_current_user(request)
    if not user: return redirect('login')

    loan = get_object_or_404(LoanRequest, pk=loan_id)

    # 1. Check if review already exists
    existing_review = ReviewAndRating.objects.filter(loan=loan, reviewer=user).first()
    if existing_review:
        messages.info(request, "You have already reviewed this transaction.")
        return render(request, 'review/review_exists.html', {'loan': loan, 'review': existing_review})

    # Determine Reviewee
    reviewee = None
    review_type = ''

    if user.user_id == loan.borrower.user_id:
        offer = loan.offers.filter(status='ACCEPTED').first()
        if offer:
            reviewee = offer.lender
            review_type = 'B2L'
    else:
        # Assuming current user is the lender from the offers
        offer = loan.offers.filter(lender=user, status='ACCEPTED').first()
        if offer:
            reviewee = loan.borrower
            review_type = 'L2B'

    if not reviewee:
        messages.error(request, "Cannot determine review target or loan not valid for review.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')

            ReviewAndRating.objects.create(
                loan=loan,
                reviewer=user,
                reviewee=reviewee,
                rating=rating,
                comment=comment,
                review_type=review_type
            )
            messages.success(request, "Review submitted successfully!")
            return redirect('reviews')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'review/create_review.html', {'loan': loan, 'reviewee': reviewee})
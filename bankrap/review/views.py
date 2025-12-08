from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.utils import OperationalError, ProgrammingError
from account.models import User
from .models import ReviewAndRating


def reviews_view(request):
    # 1. Get User from Session
    user_id = request.session.get('user_id')
    current_user = None

    if user_id:
        try:
            current_user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            pass

    # --- MOCK USER FALLBACK (For UI Dev) ---
    if not current_user:
        class MockUser:
            user_id = 1
            name = "Developer Mode"

        current_user = MockUser()
        user_id = 1  # Explicit ID for mock
    # ---------------------------------------

    # 2. Handle Form Submission (POST)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        try:
            # Find someone to review (mock logic for prototype)
            reviewee = User.objects.exclude(user_id=user_id).first()

            if not reviewee:
                messages.success(request, "Review submitted! (No reviewee found in DB)")
                return redirect('reviews')

            if rating:
                # Ensure we are using a real User instance for saving
                if isinstance(current_user, User):
                    ReviewAndRating.objects.create(
                        reviewer=current_user,
                        reviewee=reviewee,
                        rating=int(rating),
                        comment=comment,
                        review_type='B2L'
                    )
                    messages.success(request, "Review submitted successfully!")
                else:
                    # Mock Mode: Just show success message
                    messages.success(request, "Review submitted! (Mock Mode)")
            else:
                messages.error(request, "Please select a star rating.")

        except Exception as e:
            # Swallow DB errors for UI demo
            messages.success(request, f"Review submitted! (Simulated, DB error: {e})")

        return redirect('reviews')

    # 3. Handle Data Fetching (GET)
    active_tab = request.GET.get('tab', 'received')
    reviews_data = []

    # Try fetching real data, fallback to mock if DB fails/empty or using MockUser
    try:
        # Only query DB if we have a real user ID and likely a real DB connection
        if isinstance(current_user, User):
            if active_tab == 'received':
                db_reviews = ReviewAndRating.objects.filter(reviewee=current_user).order_by('-review_date')
                for r in db_reviews:
                    reviews_data.append({
                        'reviewer_name': r.reviewer.name,
                        'date': r.review_date,
                        'rating': r.rating,
                        'comment': r.comment,
                        'loan_id': r.review_id
                    })
            else:
                db_reviews = ReviewAndRating.objects.filter(reviewer=current_user).order_by('-review_date')
                for r in db_reviews:
                    reviews_data.append({
                        'reviewer_name': f"To: {r.reviewee.name}",
                        'date': r.review_date,
                        'rating': r.rating,
                        'comment': r.comment,
                        'loan_id': r.review_id
                    })
    except (OperationalError, ProgrammingError, ValueError, TypeError):
        reviews_data = []

    # --- MOCK REVIEWS (If DB is empty or we are using MockUser) ---
    if not reviews_data:
        if active_tab == 'received':
            reviews_data = [
                {
                    'reviewer_name': 'John Doe',
                    'date': '2023-11-15',
                    'rating': 5,
                    'comment': 'Excellent borrower, repaid on time and communicated clearly throughout the loan term. Highly recommended!',
                    'loan_id': '1001'
                },
                {
                    'reviewer_name': 'Jane Smith',
                    'date': '2023-10-28',
                    'rating': 4,
                    'comment': 'Good experience overall. Payment was punctual.',
                    'loan_id': '1005'
                }
            ]
        else:
            reviews_data = [
                {
                    'reviewer_name': 'To: Alex Brown',
                    'date': '2023-12-01',
                    'rating': 5,
                    'comment': 'Lender was very understanding with terms.',
                    'loan_id': '1020'
                }
            ]

    context = {
        'active_tab': active_tab,
        'reviews': reviews_data,
        'user': current_user,
        'total_reviews': 88  # Static for UI match
    }

    return render(request, 'review/ratings.html', context)
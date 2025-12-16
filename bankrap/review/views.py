from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.models import User
from loan.models import LoanRequest
from .models import ReviewAndRating
from django.db import connection
import json


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
    if not user:
        return redirect('login')

    # Fetch Reviews
    active_tab = request.GET.get('tab', 'received')
    reviews = []

    # Try using stored procedure first
    try:
        with connection.cursor() as cursor:
            if active_tab == 'received':
                cursor.callproc('GetUserReviews', [user.user_id, 'received'])
            else:
                cursor.callproc('GetUserReviews', [user.user_id, 'given'])

            # Get column names
            columns = [col[0] for col in cursor.description]

            # Convert to list of dictionaries and create proper structure for template
            reviews_data = cursor.fetchall()
            for row in reviews_data:
                review_dict = dict(zip(columns, row))

                # Create a mock loan object with loan_id attribute for template
                class MockLoan:
                    def __init__(self, loan_id, amount=None, purpose=None):
                        self.loan_id = loan_id
                        self.amount = amount
                        self.purpose = purpose

                # Create mock user objects for template compatibility
                if active_tab == 'received':
                    # Create mock reviewer object
                    class MockReviewer:
                        def __init__(self, user_id, name):
                            self.user_id = user_id
                            self.name = name

                    reviewer = MockReviewer(
                        user_id=review_dict.get('reviewer_id', 0),
                        name=review_dict.get('other_user_name', 'Unknown')
                    )

                    review_obj = type('ReviewObject', (), {
                        'review_id': review_dict.get('review_id'),
                        'rating': review_dict.get('rating'),
                        'comment': review_dict.get('comment'),
                        'review_date': review_dict.get('review_date'),
                        'review_type': review_dict.get('review_type'),
                        'reviewer': reviewer,
                        'reviewee': None,  # Not needed for received reviews
                        'loan': MockLoan(
                            loan_id=review_dict.get('loan_id', 'N/A'),
                            amount=review_dict.get('loan_amount', 0),
                            purpose=review_dict.get('loan_purpose', '')
                        )
                    })()

                else:
                    # Create mock reviewee object
                    class MockReviewee:
                        def __init__(self, user_id, name):
                            self.user_id = user_id
                            self.name = name

                    reviewee = MockReviewee(
                        user_id=review_dict.get('reviewee_id', 0),
                        name=review_dict.get('other_user_name', 'Unknown')
                    )

                    review_obj = type('ReviewObject', (), {
                        'review_id': review_dict.get('review_id'),
                        'rating': review_dict.get('rating'),
                        'comment': review_dict.get('comment'),
                        'review_date': review_dict.get('review_date'),
                        'review_type': review_dict.get('review_type'),
                        'reviewer': None,  # Not needed for given reviews
                        'reviewee': reviewee,
                        'loan': MockLoan(
                            loan_id=review_dict.get('loan_id', 'N/A'),
                            amount=review_dict.get('loan_amount', 0),
                            purpose=review_dict.get('loan_purpose', '')
                        )
                    })()

                reviews.append(review_obj)

    except Exception as e:
        print(f"Error using stored procedure: {e}")
        # Fallback to Django ORM
        if active_tab == 'received':
            reviews = ReviewAndRating.objects.filter(reviewee=user).select_related(
                'reviewer', 'reviewee', 'loan'
            ).order_by('-review_date')
        else:
            reviews = ReviewAndRating.objects.filter(reviewer=user).select_related(
                'reviewer', 'reviewee', 'loan'
            ).order_by('-review_date')

    # Calculate Trust Score using stored procedure
    avg_rating = 0
    review_count = 0
    try:
        with connection.cursor() as cursor:
            cursor.callproc('GetUserReviewStats', [user.user_id, 0, 0, 0, 0, 0, 0, 0])

            # Get OUT parameters
            cursor.execute('SELECT @_GetUserReviewStats_1, @_GetUserReviewStats_2')
            result = cursor.fetchone()

            if result:
                avg_rating = float(result[0]) if result[0] else 0.0
                review_count = result[1] if result[1] else 0
    except Exception as e:
        print(f"Error getting review stats: {e}")
        # Fallback calculation if stored procedure fails
        if not avg_rating and not review_count:
            received_all = ReviewAndRating.objects.filter(reviewee=user)
            if received_all.exists():
                avg_rating = sum([r.rating for r in received_all]) / received_all.count()
            review_count = received_all.count()

    return render(request, 'review/ratings.html', {
        'user': user,
        'reviews': reviews,
        'active_tab': active_tab,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0.0,
        'review_count': review_count
    })


def create_review(request, loan_id):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    loan = get_object_or_404(LoanRequest, pk=loan_id)

    # Check if review already exists
    existing_review = ReviewAndRating.objects.filter(loan=loan, reviewer=user).first()
    if existing_review:
        messages.info(request, "You have already reviewed this transaction.")
        return render(request, 'review/review_exists.html', {
            'loan': loan,
            'review': existing_review,
            'can_edit': True
        })

    # Determine Reviewee
    reviewee = None
    review_type = ''

    if user.user_id == loan.borrower.user_id:
        offer = loan.offers.filter(status='ACCEPTED').first()
        if offer:
            reviewee = offer.lender
            review_type = 'B2L'
    else:
        offer = loan.offers.filter(lender=user, status='ACCEPTED').first()
        if offer:
            reviewee = loan.borrower
            review_type = 'L2B'

    if not reviewee:
        messages.error(request, "Cannot determine review target or loan not valid for review.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating'))
            comment = request.POST.get('comment', '')

            # Use stored procedure
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('CreateOrUpdateReview',
                                    [loan_id, user.user_id, reviewee.user_id,
                                     rating, comment, review_type, 0, ''])

                    # Get results
                    results = cursor.fetchall()
                    if results and len(results) > 0:
                        review_data = dict(zip([col[0] for col in cursor.description], results[0]))

                        if review_data.get('action_taken') == 'created':
                            messages.success(request, "Review submitted successfully!")
                        else:
                            messages.success(request, "Review updated successfully!")

                        return redirect('reviews')
                    else:
                        raise Exception("No results from stored procedure")

            except Exception as e:
                print(f"Error using stored procedure: {e}")
                # Fallback to Django ORM
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


@require_POST
def update_review(request, review_id):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    review = get_object_or_404(ReviewAndRating, pk=review_id)

    # Check if user owns this review
    if review.reviewer != user:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
        rating = data.get('rating')
        comment = data.get('comment')

        if rating and 1 <= int(rating) <= 5:
            rating_val = int(rating)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid rating'}, status=400)

        # Try using stored procedure
        try:
            with connection.cursor() as cursor:
                cursor.callproc('CreateOrUpdateReview',
                                [review.loan.loan_id, user.user_id, review.reviewee.user_id,
                                 rating_val, comment, review.review_type, 0, ''])

                results = cursor.fetchall()
                if results and len(results) > 0:
                    review_data = dict(zip([col[0] for col in cursor.description], results[0]))

                    # Refresh the review
                    review.refresh_from_db()

                    return JsonResponse({
                        'success': True,
                        'rating': review.rating,
                        'comment': review.comment,
                        'updated_date': review.review_date.strftime('%b %d, %Y')
                    })
                else:
                    raise Exception("No results from stored procedure")

        except Exception as e:
            print(f"Error using stored procedure: {e}")
            # Fallback to Django ORM
            review.rating = rating_val
            if comment:
                review.comment = comment
            review.save()

            return JsonResponse({
                'success': True,
                'rating': review.rating,
                'comment': review.comment,
                'updated_date': review.review_date.strftime('%b %d, %Y')
            })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def delete_review(request, review_id):
    user = get_current_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)

    review = get_object_or_404(ReviewAndRating, pk=review_id)

    # Check if user owns this review
    if review.reviewer != user:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        review.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def edit_review_view(request, review_id):
    """View for editing a review (page)"""
    user = get_current_user(request)
    if not user:
        return redirect('login')

    review = get_object_or_404(ReviewAndRating, pk=review_id)

    # Check if user owns this review
    if review.reviewer != user:
        messages.error(request, "You don't have permission to edit this review.")
        return redirect('reviews')

    reviewee = review.reviewee
    loan = review.loan

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating'))
            comment = request.POST.get('comment', '')

            # Try using stored procedure
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('CreateOrUpdateReview',
                                    [loan.loan_id, user.user_id, reviewee.user_id,
                                     rating, comment, review.review_type, 0, ''])

                    results = cursor.fetchall()
                    if results and len(results) > 0:
                        messages.success(request, "Review updated successfully!")
                    else:
                        raise Exception("No results from stored procedure")

            except Exception as e:
                print(f"Error using stored procedure: {e}")
                # Fallback to Django ORM
                review.rating = rating
                review.comment = comment
                review.save()
                messages.success(request, "Review updated successfully!")

            return redirect('reviews')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'review/edit_review.html', {
        'review': review,
        'reviewee': reviewee,
        'loan': loan
    })
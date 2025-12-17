from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from account.models import User
from loan.models import LoanRequest
from .models import ReviewAndRating
from django.db import connection
import json
from datetime import datetime


def get_current_user(request):
    """Get the currently logged-in user from session"""
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None
    return None


# Helper Classes for Mock Objects
class MockLoan:
    """Mock loan object for template compatibility"""

    def __init__(self, loan_id, amount=None, purpose=None):
        self.loan_id = loan_id
        self.amount = amount
        self.purpose = purpose


class MockUser:
    """Mock user object for template compatibility"""

    def __init__(self, user_id, name, user_type=None):
        self.user_id = user_id
        self.name = name
        self.type = user_type


class ReviewObject:
    """Proper class for review objects"""

    def __init__(self, review_dict, active_tab):
        self.review_id = review_dict.get('review_id')
        self.rating = review_dict.get('rating')
        self.comment = review_dict.get('comment')
        self.review_date = review_dict.get('review_date')
        self.review_type = review_dict.get('review_type')
        self.loan = MockLoan(
            loan_id=review_dict.get('loan_id', 'N/A'),
            amount=review_dict.get('loan_amount', 0),
            purpose=review_dict.get('loan_purpose', '')
        )

        if active_tab == 'received':
            self.reviewer = MockUser(
                user_id=review_dict.get('reviewer_id', 0),
                name=review_dict.get('other_user_name', 'Unknown'),
                user_type=review_dict.get('other_user_type')
            )
            self.reviewee = None
        else:
            self.reviewee = MockUser(
                user_id=review_dict.get('reviewee_id', 0),
                name=review_dict.get('other_user_name', 'Unknown'),
                user_type=review_dict.get('other_user_type')
            )
            self.reviewer = None


def get_reviews_from_db(user, active_tab):
    """Get reviews using Django ORM as fallback"""
    if active_tab == 'received':
        return ReviewAndRating.objects.filter(reviewee=user).select_related(
            'reviewer', 'reviewee', 'loan'
        ).order_by('-review_date')
    else:
        return ReviewAndRating.objects.filter(reviewer=user).select_related(
            'reviewer', 'reviewee', 'loan'
        ).order_by('-review_date')


def get_reviews_via_stored_procedure(user, active_tab):
    """Get reviews using stored procedure"""
    reviews = []
    try:
        with connection.cursor() as cursor:
            cursor.callproc('GetUserReviews', [user.user_id, active_tab])
            columns = [col[0] for col in cursor.description]
            reviews_data = cursor.fetchall()

            for row in reviews_data:
                review_dict = dict(zip(columns, row))
                # Convert datetime if needed
                if isinstance(review_dict.get('review_date'), str):
                    try:
                        review_dict['review_date'] = datetime.strptime(
                            review_dict['review_date'], '%Y-%m-%d %H:%M:%S'
                        )
                    except:
                        pass

                review_obj = ReviewObject(review_dict, active_tab)
                reviews.append(review_obj)

        return reviews
    except Exception as e:
        print(f"Error using stored procedure GetUserReviews: {e}")
        raise


def get_review_stats(user):
    """Get review statistics using stored procedure"""
    try:
        with connection.cursor() as cursor:
            cursor.callproc('GetUserReviewStats', [user.user_id])
            result = cursor.fetchone()

            if result:
                avg_rating = float(result[0]) if result[0] else 0.0
                review_count = result[1] if result[1] else 0
                return avg_rating, review_count
    except Exception as e:
        print(f"Error using stored procedure GetUserReviewStats: {e}")

    # Fallback: calculate from Django ORM
    received_all = ReviewAndRating.objects.filter(reviewee=user)
    if received_all.exists():
        avg_rating = sum([r.rating for r in received_all]) / received_all.count()
    else:
        avg_rating = 0.0
    review_count = received_all.count()

    return avg_rating, review_count


def reviews_view(request):
    """Main view for displaying user reviews"""
    user = get_current_user(request)
    if not user:
        return redirect('login')

    active_tab = request.GET.get('tab', 'received')

    # Get reviews
    try:
        reviews = get_reviews_via_stored_procedure(user, active_tab)
    except Exception as e:
        print(f"Falling back to Django ORM due to error: {e}")
        # Fallback to Django ORM
        reviews = get_reviews_from_db(user, active_tab)

    # Get review statistics
    avg_rating, review_count = get_review_stats(user)

    return render(request, 'review/ratings.html', {
        'user': user,
        'reviews': reviews,
        'active_tab': active_tab,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0.0,
        'review_count': review_count
    })


def get_review_targets(user, loan):
    """Determine who to review and review type"""
    reviewee = None
    review_type = ''

    if user.user_id == loan.borrower.user_id:
        # Borrower reviewing lender
        offer = loan.offers.filter(status='ACCEPTED').first()
        if offer:
            reviewee = offer.lender
            review_type = 'B2L'  # Borrower to Lender
    else:
        # Lender reviewing borrower
        offer = loan.offers.filter(lender=user, status='ACCEPTED').first()
        if offer:
            reviewee = loan.borrower
            review_type = 'L2B'  # Lender to Borrower

    return reviewee, review_type


def create_review(request, loan_id):
    """Create a new review"""
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

    # Determine who to review
    reviewee, review_type = get_review_targets(user, loan)
    if not reviewee:
        messages.error(request, "Cannot determine review target or loan not valid for review.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 0))
            comment = request.POST.get('comment', '').strip()

            if not 1 <= rating <= 5:
                messages.error(request, "Rating must be between 1 and 5.")
                return render(request, 'review/create_review.html', {
                    'loan': loan,
                    'reviewee': reviewee
                })

            # Try using stored procedure
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('CreateOrUpdateReview', [
                        loan_id,
                        user.user_id,
                        reviewee.user_id,
                        rating,
                        comment,
                        review_type
                    ])

                    results = cursor.fetchall()
                    if results:
                        review_data = dict(zip(
                            [col[0] for col in cursor.description],
                            results[0]
                        ))
                        action = review_data.get('action_taken', 'created')
                        messages.success(request, f"Review {action} successfully!")
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
            messages.error(request, f"Error submitting review: {str(e)}")
            return render(request, 'review/create_review.html', {
                'loan': loan,
                'reviewee': reviewee
            })

    return render(request, 'review/create_review.html', {
        'loan': loan,
        'reviewee': reviewee
    })


@require_POST
def update_review(request, review_id):
    """Update a review via AJAX"""
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
        comment = data.get('comment', '').strip()

        if not rating or not 1 <= int(rating) <= 5:
            return JsonResponse({'success': False, 'error': 'Invalid rating'}, status=400)

        rating_val = int(rating)

        # Try using stored procedure
        try:
            with connection.cursor() as cursor:
                cursor.callproc('CreateOrUpdateReview', [
                    review.loan.loan_id,
                    user.user_id,
                    review.reviewee.user_id,
                    rating_val,
                    comment,
                    review.review_type
                ])

                results = cursor.fetchall()
                if not results:
                    raise Exception("No results from stored procedure")

        except Exception as e:
            print(f"Error using stored procedure: {e}")
            # Fallback to Django ORM
            review.rating = rating_val
            review.comment = comment
            review.save()

        # Refresh the review
        review.refresh_from_db()

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
    """Delete a review via AJAX"""
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
    """Page for editing a review"""
    user = get_current_user(request)
    if not user:
        return redirect('login')

    review = get_object_or_404(ReviewAndRating, pk=review_id)

    # Check if user owns this review
    if review.reviewer != user:
        messages.error(request, "You don't have permission to edit this review.")
        return redirect('reviews')

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating', 0))
            comment = request.POST.get('comment', '').strip()

            if not 1 <= rating <= 5:
                messages.error(request, "Rating must be between 1 and 5.")
                return render(request, 'review/edit_review.html', {
                    'review': review,
                    'reviewee': review.reviewee,
                    'loan': review.loan
                })

            # Try using stored procedure
            try:
                with connection.cursor() as cursor:
                    cursor.callproc('CreateOrUpdateReview', [
                        review.loan.loan_id,
                        user.user_id,
                        review.reviewee.user_id,
                        rating,
                        comment,
                        review.review_type
                    ])

                    results = cursor.fetchall()
                    if results:
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
            messages.error(request, f"Error updating review: {str(e)}")

    return render(request, 'review/edit_review.html', {
        'review': review,
        'reviewee': review.reviewee,
        'loan': review.loan
    })
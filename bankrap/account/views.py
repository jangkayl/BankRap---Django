from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from .models import User, BorrowerProfile, LenderProfile
from wallet.models import Wallet, WalletTransaction
from review.models import ReviewAndRating
from loan.models import LoanRequest, LoanOffer, ActiveLoan
from transaction.models import Transaction


# --- Helper Function ---
def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = User.objects.get(user_id=user_id)
            if user.type == 'B':
                try:
                    return BorrowerProfile.objects.get(user_id=user_id)
                except BorrowerProfile.DoesNotExist:
                    return user
            elif user.type == 'L':
                try:
                    return LenderProfile.objects.get(user_id=user_id)
                except LenderProfile.DoesNotExist:
                    return user
            return user
        except User.DoesNotExist:
            return None
    return None


# --- Dashboard View ---
def dashboard_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    # Get user's wallet
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=user, balance=0.00)

    # Calculate statistics based on user type
    if user.type == 'B':  # Borrower
        # Get borrower's loan requests
        loan_requests = LoanRequest.objects.filter(borrower=user)

        # Count pending requests
        pending_requests_count = loan_requests.filter(status='PENDING').count()

        # Sum total amount of pending requests
        pending_requests_total = loan_requests.filter(status='PENDING').aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Get offers made to borrower's requests
        offers_to_me = LoanOffer.objects.filter(
            loan_request__borrower=user,
            status='PENDING'
        ).count()

        # Sum total offered amount
        offers_total = LoanOffer.objects.filter(
            loan_request__borrower=user,
            status='PENDING'
        ).aggregate(
            total=Sum('offered_amount')
        )['total'] or 0

        # Get active loans
        active_loans = ActiveLoan.objects.filter(borrower=user, status='ACTIVE')

        # Calculate upcoming repayments
        upcoming_repayments = active_loans.count()

        # Calculate total due soon (next 7 days)
        due_date_threshold = timezone.now().date() + timedelta(days=7)
        due_soon_amount = 0
        for loan in active_loans:
            if loan.due_date <= due_date_threshold:
                # Calculate monthly payment for demonstration
                # In real app, you'd have proper repayment calculation
                due_soon_amount += loan.principal_amount / 12  # Simplified

    else:  # Lender
        # Get lender's offers
        my_offers = LoanOffer.objects.filter(lender=user)

        # Count pending offers
        pending_requests_count = my_offers.filter(status='PENDING').count()

        # Sum total offered amount
        pending_requests_total = my_offers.filter(status='PENDING').aggregate(
            total=Sum('offered_amount')
        )['total'] or 0

        # Get offers made to lender's loan requests (if any)
        offers_to_me = LoanOffer.objects.filter(
            loan_request__borrower=user,
            status='PENDING'
        ).count()  # Usually 0 for lenders

        # Sum total offered amount to lender
        offers_total = LoanOffer.objects.filter(
            loan_request__borrower=user,
            status='PENDING'
        ).aggregate(
            total=Sum('offered_amount')
        )['total'] or 0

        # Get active loans where lender is investor
        active_loans = ActiveLoan.objects.filter(lender=user, status='ACTIVE')

        # Calculate upcoming repayments (from borrower to lender)
        upcoming_repayments = active_loans.count()

        # Calculate total to receive soon (next 7 days)
        due_date_threshold = timezone.now().date() + timedelta(days=7)
        due_soon_amount = 0
        for loan in active_loans:
            if loan.due_date <= due_date_threshold:
                # Calculate repayment to receive
                due_soon_amount += loan.principal_amount / 12  # Simplified

    # Get recent notifications (simplified - in real app, use Notification model)
    # For now, we'll show recent activities
    recent_activities = []

    # Get recent transactions
    recent_transactions = Transaction.objects.filter(user=user).order_by('-transaction_date')[:3]
    for trans in recent_transactions:
        recent_activities.append({
            'type': 'transaction',
            'title': f"{trans.get_type_display()} {'Completed' if trans.status == 'C' else trans.get_status_display()}",
            'description': f"Amount: ₱{trans.amount}",
            'time': 'Recently',
            'icon': 'check' if trans.status == 'C' else 'info'
        })

    # Get recent loan status changes
    if user.type == 'B':
        recent_loans = LoanRequest.objects.filter(borrower=user).order_by('-request_date')[:2]
        for loan in recent_loans:
            if loan.status == 'FUNDED':
                recent_activities.append({
                    'type': 'loan',
                    'title': 'Loan Funded',
                    'description': f"Your loan request #{loan.loan_id} has been funded",
                    'time': 'Recently',
                    'icon': 'dollar-sign'
                })
    else:
        recent_offers = LoanOffer.objects.filter(lender=user).order_by('-offer_date')[:2]
        for offer in recent_offers:
            if offer.status == 'ACCEPTED':
                recent_activities.append({
                    'type': 'offer',
                    'title': 'Offer Accepted',
                    'description': f"Your offer for loan #{offer.loan_request.loan_id} was accepted",
                    'time': 'Recently',
                    'icon': 'check-circle'
                })

    context = {
        'user': user,
        'wallet': wallet,
        'pending_requests_count': pending_requests_count,
        'pending_requests_total': pending_requests_total,
        'offers_to_me': offers_to_me,
        'offers_total': offers_total,
        'upcoming_repayments': upcoming_repayments,
        'due_soon_amount': due_soon_amount,
        'recent_activities': recent_activities[:3],  # Limit to 3 most recent
    }

    return render(request, 'account/dashboard.html', context)


# --- Other views remain the same ---
def profile_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        try:
            user.name = request.POST.get('name')
            user.address = request.POST.get('address')
            user.contact_number = request.POST.get('contact_number')
            user.email = request.POST.get('email')

            # Handle file upload
            if 'school_id_file' in request.FILES:
                user.school_id_file = request.FILES['school_id_file']

            if user.type == 'B':
                income_str = request.POST.get('income')
                if income_str and income_str.strip():
                    user.income = income_str
                else:
                    user.income = 0
                user.employment_status = request.POST.get('employment_status')

            elif user.type == 'L':
                min_inv_str = request.POST.get('min_investment_amount')
                if min_inv_str and min_inv_str.strip():
                    user.min_investment_amount = min_inv_str
                else:
                    user.min_investment_amount = 0

                # Handle available funds for lenders
                available_funds_str = request.POST.get('available_funds')
                if available_funds_str and available_funds_str.strip():
                    user.available_funds = available_funds_str

                user.investment_preference = request.POST.get('investment_preference')

            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')

        except Exception as e:
            messages.error(request, f"Error updating profile: {e}")

    # --- Trust Score Calculation for Own Profile ---
    reviews_received = ReviewAndRating.objects.filter(reviewee=user)
    avg_rating = reviews_received.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = 0.0

    review_count = reviews_received.count()

    # --- Additional Dynamic Statistics ---

    # Get user's wallet
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=user, balance=0.00)

    # Loan statistics based on user type
    if user.type == 'B':
        # Borrower statistics
        loan_requests = LoanRequest.objects.filter(borrower=user)
        total_requests = loan_requests.count()
        funded_requests = loan_requests.filter(status='FUNDED').count()
        repaid_loans = loan_requests.filter(status='REPAID').count()

        # Active loans
        active_loans = ActiveLoan.objects.filter(borrower=user, status='ACTIVE')
        total_active_loans = active_loans.count()

        # Calculate total borrowed amount
        total_borrowed = loan_requests.filter(status__in=['FUNDED', 'REPAID']).aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Calculate total repaid amount (simplified)
        total_repaid = total_borrowed * 0.7  # Assuming 70% repayment for demo

        # Get recent loan requests
        recent_requests = loan_requests.order_by('-request_date')[:5]

        user_stats = {
            'total_requests': total_requests,
            'funded_requests': funded_requests,
            'repaid_loans': repaid_loans,
            'total_active_loans': total_active_loans,
            'total_borrowed': total_borrowed,
            'total_repaid': total_repaid,
            'recent_requests': recent_requests,
        }

    else:
        # Lender statistics
        loan_offers = LoanOffer.objects.filter(lender=user)
        total_offers = loan_offers.count()
        accepted_offers = loan_offers.filter(status='ACCEPTED').count()

        # Active investments
        active_investments = ActiveLoan.objects.filter(lender=user, status='ACTIVE')
        total_active_investments = active_investments.count()

        # Calculate total invested amount
        total_invested = active_investments.aggregate(
            total=Sum('principal_amount')
        )['total'] or 0

        # Calculate total returns (simplified)
        total_returns = total_invested * 0.15  # Assuming 15% return for demo

        # Get successful investments (loans that have been repaid)
        successful_investments = ActiveLoan.objects.filter(
            lender=user,
            status='PAID'
        ).count()

        # Get recent offers
        recent_offers = loan_offers.order_by('-offer_date')[:5]

        user_stats = {
            'total_offers': total_offers,
            'accepted_offers': accepted_offers,
            'total_active_investments': total_active_investments,
            'total_invested': total_invested,
            'total_returns': total_returns,
            'successful_investments': successful_investments,
            'recent_offers': recent_offers,
        }

    # Get recent reviews
    recent_reviews = reviews_received.order_by('-review_date')[:3]

    # Calculate member since
    if hasattr(user, 'profile_created_date'):
        member_since = user.profile_created_date
    else:
        # Fallback to user creation or current date
        member_since = timezone.now().date()

    context = {
        'user': user,
        'wallet': wallet,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'recent_reviews': recent_reviews,
        'member_since': member_since,
        'user_stats': user_stats,
    }

    return render(request, 'account/profile.html', context)


def public_profile_view(request, user_id):
    """
    Public view of a user's profile.
    """
    # 1. Get the current logged-in user (viewer)
    viewer_id = request.session.get('user_id')
    if not viewer_id:
        return redirect('login')

    # 2. Get the target user (profile owner)
    target_user = get_object_or_404(User, pk=user_id)

    # Get the specific profile type if available
    if target_user.type == 'B':
        try:
            target_user = BorrowerProfile.objects.get(user_id=user_id)
        except BorrowerProfile.DoesNotExist:
            pass
    elif target_user.type == 'L':
        try:
            target_user = LenderProfile.objects.get(user_id=user_id)
        except LenderProfile.DoesNotExist:
            pass

    # 3. Get Reviews & Score
    reviews_received = ReviewAndRating.objects.filter(reviewee=target_user).order_by('-review_date')
    avg_rating = reviews_received.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = 0.0
    review_count = reviews_received.count()

    # 4. Get Open Requests (Only if target is Borrower)
    open_requests = []
    if target_user.type == 'B':
        open_requests = LoanRequest.objects.filter(borrower=target_user, status='PENDING').order_by('-request_date')

    # 5. Get additional statistics based on user type
    if target_user.type == 'B':
        # Borrower statistics
        loan_requests = LoanRequest.objects.filter(borrower=target_user)
        total_requests = loan_requests.count()
        funded_requests = loan_requests.filter(status='FUNDED').count()
        repaid_loans = loan_requests.filter(status='REPAID').count()

        # Active loans
        active_loans = ActiveLoan.objects.filter(borrower=target_user, status='ACTIVE')
        total_active_loans = active_loans.count()

        # Calculate total borrowed amount
        total_borrowed = loan_requests.filter(status__in=['FUNDED', 'REPAID']).aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Calculate repayment rate (simplified)
        repayment_rate = 0
        if funded_requests > 0:
            repayment_rate = (repaid_loans / funded_requests) * 100

        user_stats = {
            'total_requests': total_requests,
            'funded_requests': funded_requests,
            'repaid_loans': repaid_loans,
            'total_active_loans': total_active_loans,
            'total_borrowed': total_borrowed,
            'repayment_rate': round(repayment_rate, 1),
            'credit_score': target_user.credit_score if hasattr(target_user, 'credit_score') else 0,
            'income': target_user.income if hasattr(target_user, 'income') else 0,
            'employment_status': target_user.employment_status if hasattr(target_user,
                                                                          'employment_status') else 'Not specified',
        }

    else:
        # Lender statistics
        loan_offers = LoanOffer.objects.filter(lender=target_user)
        total_offers = loan_offers.count()
        accepted_offers = loan_offers.filter(status='ACCEPTED').count()

        # Active investments
        active_investments = ActiveLoan.objects.filter(lender=target_user, status='ACTIVE')
        total_active_investments = active_investments.count()

        # Calculate total invested amount
        total_invested = active_investments.aggregate(
            total=Sum('principal_amount')
        )['total'] or 0

        # Calculate total returns (completed loans)
        completed_investments = ActiveLoan.objects.filter(lender=target_user, status='PAID')
        successful_investments = completed_investments.count()

        # Calculate acceptance rate
        acceptance_rate = 0
        if total_offers > 0:
            acceptance_rate = (accepted_offers / total_offers) * 100

        user_stats = {
            'total_offers': total_offers,
            'accepted_offers': accepted_offers,
            'total_active_investments': total_active_investments,
            'total_invested': total_invested,
            'successful_investments': successful_investments,
            'acceptance_rate': round(acceptance_rate, 1),
            'available_funds': target_user.available_funds if hasattr(target_user, 'available_funds') else 0,
            'min_investment_amount': target_user.min_investment_amount if hasattr(target_user,
                                                                                  'min_investment_amount') else 0,
            'investment_preference': target_user.investment_preference if hasattr(target_user,
                                                                                  'investment_preference') else 'Not specified',
        }

    # 6. Get recent successful transactions (for both types)
    recent_successful_loans = []
    if target_user.type == 'B':
        recent_successful_loans = LoanRequest.objects.filter(
            borrower=target_user,
            status='REPAID'
        ).order_by('-request_date')[:3]
    else:
        recent_successful_loans = ActiveLoan.objects.filter(
            lender=target_user,
            status='PAID'
        ).select_related('loan_request').order_by('-start_date')[:3]

    # 7. Calculate member since
    if hasattr(target_user, 'profile_created_date'):
        member_since = target_user.profile_created_date
    else:
        member_since = timezone.now().date()

    # 8. Check if viewer is looking at their own profile
    is_own_profile = (int(viewer_id) == int(user_id))

    context = {
        'profile_user': target_user,  # The user being viewed
        'avg_rating': avg_rating,
        'review_count': review_count,
        'reviews': reviews_received[:5],  # Limit to 5 most recent
        'open_requests': open_requests,
        'viewer_id': viewer_id,
        'user_stats': user_stats,
        'recent_successful_loans': recent_successful_loans,
        'member_since': member_since,
        'is_own_profile': is_own_profile,
        'current_year': timezone.now().year,
    }

    return render(request, 'account/public_profile.html', context)

def login_view(request):
    if request.method == 'POST':
        identity = request.POST.get('identity')
        password = request.POST.get('password')

        try:
            user = User.objects.filter(Q(email=identity) | Q(student_id=identity), password=password).first()
            if user:
                request.session['user_id'] = user.user_id
                messages.success(request, f"Welcome back, {user.name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials.")
        except Exception as e:
            messages.error(request, f"Login Error: {e}")

    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        student_id = request.POST.get('student_id')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address', '')
        contact = request.POST.get('contact_number', '')
        role = request.POST.get('role')
        school_id_file = request.FILES.get('school_id_file')

        try:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return render(request, 'register.html')

            if User.objects.filter(student_id=student_id).exists():
                messages.error(request, "Student ID already registered.")
                return render(request, 'register.html')

            new_user = None

            if role == 'L':
                new_user = LenderProfile.objects.create(
                    name=name,
                    email=email,
                    password=password,
                    student_id=student_id,
                    address=address,
                    contact_number=contact,
                    type='L',
                    school_id_file=school_id_file,
                    min_investment_amount=500.00
                )
            else:
                new_user = BorrowerProfile.objects.create(
                    name=name,
                    email=email,
                    password=password,
                    student_id=student_id,
                    address=address,
                    contact_number=contact,
                    type='B',
                    school_id_file=school_id_file,
                    credit_score=0
                )

            Wallet.objects.create(user=new_user, balance=0.00)
            request.session['user_id'] = new_user.user_id

            messages.success(request, "Account created successfully!")
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f"Registration failed: {e}")

    return render(request, 'register.html')


def logout_view(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('login')


class AccountView(View):
    template_name = 'account.html'

    def get(self, request):
        accounts = User.objects.all()
        return render(request, self.template_name, {'accounts': accounts})


def messaging_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    # Mock data
    conversations = [
        {'name': 'Maria Santos', 'last_message': 'Hello...', 'time': '2 min ago', 'unread': 2, 'online': True,
         'active': True}]
    return render(request, 'account/messaging.html', {'conversations': conversations, 'user': user})


def settings_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        # --- 1. Change Password Logic ---
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        password_changed = False
        email_changed = False

        try:
            # Check Password
            if current_password:
                if user.password != current_password:
                    messages.error(request, "Incorrect current password.")
                elif new_password != confirm_password:
                    messages.error(request, "New passwords do not match.")
                elif not new_password:
                    messages.error(request, "Please enter a new password.")
                else:
                    user.password = new_password
                    password_changed = True

            # --- 2. Change Email Logic ---
            new_email = request.POST.get('new_email')
            if new_email and new_email != user.email:
                # Ensure email isn't taken by someone else
                if User.objects.filter(email=new_email).exclude(user_id=user.user_id).exists():
                    messages.error(request, "This email address is already in use.")
                else:
                    user.email = new_email
                    email_changed = True

            # --- Save Changes ---
            if password_changed or email_changed:
                user.save()
                if password_changed:
                    messages.success(request, "Password updated successfully.")
                if email_changed:
                    messages.success(request, "Email updated successfully.")
            elif not current_password and not (new_email and new_email != user.email):
                # No relevant fields filled for password/email change
                # Only show "No changes" if nothing was attempted (i.e. empty form submit)
                # But since we check if fields exist, maybe just pass if nothing happened
                pass

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

        return redirect('settings')

    return render(request, 'account/settings.html', {'user': user})


def notifications_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    return render(request, 'account/notifications.html', {'user': user})
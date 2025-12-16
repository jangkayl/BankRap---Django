from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from decimal import Decimal
from django.views.decorators.http import require_POST
from django.db import connection
from django.db.utils import DatabaseError

from .models import User, BorrowerProfile, LenderProfile, Message, Notification
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


# --- Helper Functions for Stored Procedures ---
def execute_stored_procedure(proc_name, params=None):
    """Execute a stored procedure and return the results."""
    try:
        with connection.cursor() as cursor:
            # Build the SQL query
            if params:
                placeholders = ', '.join(['%s'] * len(params))
                sql = f"CALL {proc_name}({placeholders})"
                cursor.execute(sql, params)
            else:
                sql = f"CALL {proc_name}()"
                cursor.execute(sql)

            # Fetch all results
            results = []
            while True:
                rows = cursor.fetchall()
                if rows:
                    # Get column names
                    columns = [col[0] for col in cursor.description]
                    result_set = [dict(zip(columns, row)) for row in rows]
                    results.append(result_set)
                if not cursor.nextset():
                    break

            return results
    except DatabaseError as e:
        print(f"Database error in {proc_name}: {e}")
        return None
    except Exception as e:
        print(f"Error executing {proc_name}: {e}")
        return None


def execute_stored_procedure_with_out_params(proc_name, in_params, out_param_names):
    """Execute a stored procedure with OUT parameters."""
    try:
        with connection.cursor() as cursor:
            # Prepare the call
            in_placeholders = ', '.join(['%s'] * len(in_params))
            out_placeholders = ', '.join(['@' + name for name in out_param_names])
            placeholders = ', '.join([in_placeholders, out_placeholders]) if in_params else out_placeholders

            # Execute the stored procedure
            if in_params:
                cursor.execute(f"CALL {proc_name}({placeholders})", in_params)
            else:
                cursor.execute(f"CALL {proc_name}({placeholders})")

            # Get OUT parameter values
            out_values = {}
            for name in out_param_names:
                cursor.execute(f"SELECT @{name}")
                out_values[name] = cursor.fetchone()[0]

            # Get any result sets
            results = []
            while True:
                rows = cursor.fetchall()
                if rows:
                    columns = [col[0] for col in cursor.description]
                    result_set = [dict(zip(columns, row)) for row in rows]
                    results.append(result_set)
                if not cursor.nextset():
                    break

            return results, out_values
    except DatabaseError as e:
        print(f"Database error in {proc_name}: {e}")
        return None, None


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

    # --- Trust Score Calculation using Stored Procedure ---
    try:
        # Use stored procedure to get review statistics
        results, out_values = execute_stored_procedure_with_out_params(
            'GetUserReviewStats',
            [user.user_id],
            ['p_avg_rating', 'p_total_reviews', 'p_5_star', 'p_4_star', 'p_3_star', 'p_2_star', 'p_1_star']
        )

        if results and out_values:
            avg_rating = float(out_values.get('p_avg_rating', 0))
            review_count = out_values.get('p_total_reviews', 0)

            # Get detailed breakdown from result set
            if results and len(results) > 0 and len(results[0]) > 0:
                review_stats = results[0][0]
        else:
            # Fallback to Django ORM if stored procedure fails
            reviews_received = ReviewAndRating.objects.filter(reviewee=user)
            avg_rating = reviews_received.aggregate(Avg('rating'))['rating__avg']
            if avg_rating:
                avg_rating = round(avg_rating, 1)
            else:
                avg_rating = 0.0
            review_count = reviews_received.count()
    except Exception as e:
        print(f"Error getting review stats: {e}")
        # Fallback to Django ORM
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
        wallet = Wallet.objects.create(user=user, balance=Decimal('0.00'))

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
        total_borrowed_result = loan_requests.filter(status__in=['FUNDED', 'REPAID']).aggregate(
            total=Sum('amount')
        )
        total_borrowed = total_borrowed_result['total'] or Decimal('0')

        # Calculate total repaid amount (simplified)
        total_repaid = total_borrowed * Decimal('0.7')  # Assuming 70% repayment for demo

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
        total_invested_result = active_investments.aggregate(
            total=Sum('principal_amount')
        )
        total_invested = total_invested_result['total'] or Decimal('0')

        # Calculate total returns (simplified)
        total_returns = total_invested * Decimal('0.15')  # Assuming 15% return for demo

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
    recent_reviews = ReviewAndRating.objects.filter(reviewee=user).order_by('-review_date')[:3]

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

    # 3. Get Reviews & Score using Stored Procedure
    try:
        results, out_values = execute_stored_procedure_with_out_params(
            'GetUserReviewStats',
            [target_user.user_id],
            ['p_avg_rating', 'p_total_reviews', 'p_5_star', 'p_4_star', 'p_3_star', 'p_2_star', 'p_1_star']
        )

        if results and out_values:
            avg_rating = float(out_values.get('p_avg_rating', 0))
            review_count = out_values.get('p_total_reviews', 0)
        else:
            # Fallback to Django ORM
            reviews_received = ReviewAndRating.objects.filter(reviewee=target_user)
            avg_rating = reviews_received.aggregate(Avg('rating'))['rating__avg']
            if avg_rating:
                avg_rating = round(avg_rating, 1)
            else:
                avg_rating = 0.0
            review_count = reviews_received.count()
    except Exception as e:
        print(f"Error getting review stats: {e}")
        # Fallback to Django ORM
        reviews_received = ReviewAndRating.objects.filter(reviewee=target_user)
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

    # 9. Get recent reviews for display
    recent_reviews = ReviewAndRating.objects.filter(reviewee=target_user).order_by('-review_date')[:5]

    context = {
        'profile_user': target_user,  # The user being viewed
        'avg_rating': avg_rating,
        'review_count': review_count,
        'reviews': recent_reviews,  # Limit to 5 most recent
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

    # Get the conversation partner (from URL parameter or default)
    partner_id = request.GET.get('with')
    partner = None
    active_chat_id = None

    # Get conversations using stored procedure
    conversations = []
    try:
        results = execute_stored_procedure('GetUserConversations', [user.user_id, partner_id])
        if results and len(results) > 0:
            conversations = results[0]
    except Exception as e:
        print(f"Error getting conversations: {e}")
        # Fallback to Django ORM
        # Get all users the current user has messaged with
        sent_to = User.objects.filter(
            received_messages__sender=user
        ).distinct()

        received_from = User.objects.filter(
            sent_messages__receiver=user
        ).distinct()

        # Combine and remove duplicates
        all_partners = (sent_to | received_from).distinct()

        # Format conversations for the sidebar
        for partner_user in all_partners:
            # Get last message in conversation
            last_message = Message.objects.filter(
                (Q(sender=user) & Q(receiver=partner_user)) |
                (Q(sender=partner_user) & Q(receiver=user))
            ).order_by('-created_at').first()

            # Count unread messages from this partner
            unread_count = Message.objects.filter(
                sender=partner_user,
                receiver=user,
                is_read=False
            ).count()

            conversations.append({
                'user_id': partner_user.user_id,
                'name': partner_user.name,
                'last_message': last_message.content[:50] + "..." if last_message else "No messages yet",
                'time': last_message.created_at.strftime("%I:%M %p") if last_message else "",
                'unread_count': unread_count,
                'online': False,
                'is_active': str(partner_user.user_id) == partner_id
            })

    # Get messages with selected partner using stored procedure
    messages_list = []
    if partner_id:
        try:
            partner = User.objects.get(user_id=partner_id)
            # Use stored procedure to get messages
            try:
                results = execute_stored_procedure('GetConversationMessages',
                                                   [user.user_id, partner.user_id, 0, 50])
                if results and len(results) > 0:
                    messages_list = results[0]

                    # Convert the stored procedure results to a format compatible with template
                    for msg in messages_list:
                        msg['sender'] = {'user_id': msg['sender_id'], 'name': msg['sender_name']}
                        msg['receiver'] = {'user_id': msg['receiver_id'], 'name': msg['receiver_name']}
                else:
                    # Fallback to Django ORM
                    messages_list = Message.objects.filter(
                        (Q(sender=user) & Q(receiver=partner)) |
                        (Q(sender=partner) & Q(receiver=user))
                    ).order_by('created_at')
            except Exception as e:
                print(f"Error getting messages via stored procedure: {e}")
                # Fallback to Django ORM
                messages_list = Message.objects.filter(
                    (Q(sender=user) & Q(receiver=partner)) |
                    (Q(sender=partner) & Q(receiver=user))
                ).order_by('created_at')

        except User.DoesNotExist:
            messages_list = []

    # Handle message sending using stored procedure
    if request.method == 'POST' and partner:
        content = request.POST.get('content', '').strip()
        if content:
            try:
                # Use stored procedure to create message with notification
                with connection.cursor() as cursor:
                    cursor.callproc('CreateMessageWithNotification',
                                    [user.user_id, partner.user_id, content, 0, 0])
                    cursor.execute('SELECT @_CreateMessageWithNotification_4')
                    result = cursor.fetchone()

                    if result:
                        message_id = result[0]
                        messages.success(request, "Message sent!")
                    else:
                        # Fallback to Django ORM
                        new_message = Message.objects.create(
                            sender=user,
                            receiver=partner,
                            content=content
                        )
                        # Create notification for the receiver
                        Notification.objects.create(
                            user=partner,
                            notification_type='MESSAGE',
                            title=f'New Message from {user.name}',
                            message=f'{content[:100]}...' if len(content) > 100 else content,
                            priority='MEDIUM'
                        )
                        message_id = new_message.message_id

                return redirect(f'{request.path}?with={partner.user_id}')
            except Exception as e:
                print(f"Error sending message via stored procedure: {e}")
                # Fallback to Django ORM
                new_message = Message.objects.create(
                    sender=user,
                    receiver=partner,
                    content=content
                )
                # Create notification for the receiver
                Notification.objects.create(
                    user=partner,
                    notification_type='MESSAGE',
                    title=f'New Message from {user.name}',
                    message=f'{content[:100]}...' if len(content) > 100 else content,
                    priority='MEDIUM'
                )
                return redirect(f'{request.path}?with={partner.user_id}')
        else:
            messages.error(request, "Message cannot be empty")

    return render(request, 'account/messaging.html', {
        'user': user,
        'conversations': conversations,
        'partner': partner,
        'messages': messages_list,
        'active_chat_id': partner_id
    })


def get_new_messages(request):
    """AJAX endpoint to get new messages using stored procedure"""
    user = get_current_user(request)
    if not user:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    partner_id = request.GET.get('partner_id')
    last_message_id = request.GET.get('last_message_id', 0)

    try:
        partner = User.objects.get(user_id=partner_id)

        # Use stored procedure to get new messages
        try:
            results = execute_stored_procedure('GetConversationMessages',
                                               [user.user_id, partner.user_id, last_message_id, 100])

            if results and len(results) > 0:
                messages_data = results[0]

                formatted_messages = []
                for msg in messages_data:
                    formatted_messages.append({
                        'id': msg['message_id'],
                        'sender_id': msg['sender_id'],
                        'sender_name': msg['sender_name'],
                        'content': msg['content'],
                        'time': msg['created_at'].strftime("%I:%M %p") if isinstance(msg['created_at'], datetime) else
                        msg['created_at'],
                        'date': msg['created_at'].strftime("%b %d") if isinstance(msg['created_at'], datetime) else ""
                    })

                return JsonResponse({
                    'success': True,
                    'messages': formatted_messages,
                    'has_new': len(formatted_messages) > 0
                })
        except Exception as e:
            print(f"Error getting new messages via stored procedure: {e}")
            # Fallback to Django ORM
            new_messages = Message.objects.filter(
                (Q(sender=user) & Q(receiver=partner)) |
                (Q(sender=partner) & Q(receiver=user)),
                message_id__gt=last_message_id
            ).order_by('created_at')

            # Mark as read
            Message.objects.filter(sender=partner, receiver=user, is_read=False).update(is_read=True)

            messages_data = []
            for msg in new_messages:
                messages_data.append({
                    'id': msg.message_id,
                    'sender_id': msg.sender.user_id,
                    'content': msg.content,
                    'time': msg.created_at.strftime("%I:%M %p"),
                    'date': msg.created_at.strftime("%b %d")
                })

            return JsonResponse({
                'success': True,
                'messages': messages_data,
                'has_new': len(messages_data) > 0
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def start_conversation(request, user_id):
    """Start a new conversation with a user"""
    user = get_current_user(request)
    if not user:
        return redirect('login')

    try:
        partner = User.objects.get(user_id=user_id)
        return redirect(f'/messages/?with={partner.user_id}')
    except User.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('dashboard')


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

    # Get filter from query parameters
    filter_type = request.GET.get('filter', 'all')
    mark_all = request.GET.get('mark_all', False)
    delete_all_read = request.GET.get('delete_all_read', False)

    # Mark all as read if requested
    if mark_all:
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read!")
        return redirect('notifications')

    # Delete all read notifications if requested
    if delete_all_read:
        deleted_count, _ = Notification.objects.filter(user=user, is_read=True).delete()
        messages.success(request, f"Deleted {deleted_count} read notifications!")
        return redirect('notifications')

    # Get notifications using stored procedure
    notifications = []
    counts = {
        'all': 0,
        'unread': 0,
        'read': 0,
        'loan_actions': 0,
        'verifications': 0,
        'messages': 0
    }

    try:
        results = execute_stored_procedure('GetUserNotifications',
                                           [user.user_id, filter_type, 50, 0])

        if results and len(results) >= 2:
            # First result set contains notifications
            notifications = results[0]
            # Second result set contains counts
            if len(results) > 1 and len(results[1]) > 0:
                count_row = results[1][0]
                counts = {
                    'all': count_row.get('all_count', 0),
                    'unread': count_row.get('unread_count', 0),
                    'read': count_row.get('read_count', 0),
                    'loan_actions': count_row.get('loan_actions_count', 0),
                    'verifications': count_row.get('verifications_count', 0),
                    'messages': count_row.get('messages_count', 0)
                }
    except Exception as e:
        print(f"Error getting notifications via stored procedure: {e}")
        # Fallback to Django ORM
        notifications_qs = Notification.objects.filter(user=user)

        # Apply filters
        if filter_type == 'unread':
            notifications_qs = notifications_qs.filter(is_read=False)
        elif filter_type == 'loan_actions':
            notification_types = ['LOAN_APPROVED', 'LOAN_OFFER', 'OFFER_ACCEPTED', 'LOAN_FUNDED', 'LOAN_REJECTED']
            notifications_qs = notifications_qs.filter(notification_type__in=notification_types)
        elif filter_type == 'verifications':
            notifications_qs = notifications_qs.filter(notification_type='VERIFICATION')
        elif filter_type == 'messages':
            notifications_qs = notifications_qs.filter(notification_type='MESSAGE')

        # Order by creation date (newest first)
        notifications = list(notifications_qs.order_by('-created_at'))

        # Get counts for filter tabs
        counts = {
            'all': Notification.objects.filter(user=user).count(),
            'unread': Notification.objects.filter(user=user, is_read=False).count(),
            'read': Notification.objects.filter(user=user, is_read=True).count(),
            'loan_actions': Notification.objects.filter(
                user=user,
                notification_type__in=['LOAN_APPROVED', 'LOAN_OFFER', 'OFFER_ACCEPTED', 'LOAN_FUNDED', 'LOAN_REJECTED']
            ).count(),
            'verifications': Notification.objects.filter(user=user, notification_type='VERIFICATION').count(),
            'messages': Notification.objects.filter(user=user, notification_type='MESSAGE').count()
        }

    context = {
        'user': user,
        'notifications': notifications,
        'filter_type': filter_type,
        'counts': counts
    }

    return render(request, 'account/notifications.html', context)


@require_POST
def mark_notification_read(request, notification_id):
    user = get_current_user(request)

    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not user:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'redirect': '/login/'
            }, status=401)
        else:
            messages.error(request, "Please log in to continue.")
            return redirect('login')

    try:
        # Try using stored procedure for batch update (single notification)
        notification_ids = str(notification_id)
        try:
            results = execute_stored_procedure('BatchUpdateNotifications',
                                               [user.user_id, notification_ids, 'read'])
            if is_ajax:
                return JsonResponse({'success': True})
            else:
                messages.success(request, "Notification marked as read!")
                return redirect('notifications')
        except Exception as e:
            print(f"Error using stored procedure: {e}")
            # Fallback to Django ORM
            notification = Notification.objects.get(notification_id=notification_id, user=user)
            notification.is_read = True
            notification.save()

            if is_ajax:
                return JsonResponse({'success': True})
            else:
                messages.success(request, "Notification marked as read!")
                return redirect('notifications')

    except Notification.DoesNotExist:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
        else:
            messages.error(request, "Notification not found!")
            return redirect('notifications')
    except Exception as e:
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            messages.error(request, f"Error marking notification as read: {e}")
            return redirect('notifications')


@require_POST
def delete_notification(request, notification_id):
    user = get_current_user(request)

    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not user:
        if is_ajax:
            # Return JSON for AJAX requests
            return JsonResponse({
                'success': False,
                'error': 'Authentication required',
                'redirect': '/login/'  # Tell frontend to redirect
            }, status=401)
        else:
            # Redirect for normal requests
            messages.error(request, "Please log in to continue.")
            return redirect('login')

    try:
        # Try using stored procedure for batch delete (single notification)
        notification_ids = str(notification_id)
        try:
            results = execute_stored_procedure('BatchUpdateNotifications',
                                               [user.user_id, notification_ids, 'delete'])
            if is_ajax:
                return JsonResponse({'success': True})
            else:
                messages.success(request, "Notification deleted!")
                return redirect('notifications')
        except Exception as e:
            print(f"Error using stored procedure: {e}")
            # Fallback to Django ORM
            notification = Notification.objects.get(notification_id=notification_id, user=user)
            notification.delete()

            if is_ajax:
                return JsonResponse({'success': True})
            else:
                messages.success(request, "Notification deleted!")
                return redirect('notifications')

    except Notification.DoesNotExist:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
        else:
            messages.error(request, "Notification not found!")
            return redirect('notifications')
    except Exception as e:
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            messages.error(request, f"Error deleting notification: {e}")
            return redirect('notifications')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.db.models import Q, Avg
from .models import User, BorrowerProfile, LenderProfile
from wallet.models import Wallet, WalletTransaction
from review.models import ReviewAndRating
from loan.models import LoanRequest, ActiveLoan, LoanOffer


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


# --- Views ---

def dashboard_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

        # --- Fetch Counts for Dashboard Stats ---

    # 1. Total Transactions Count
    # We count wallet transactions as they represent all financial activity
    transaction_count = 0
    if hasattr(user, 'wallet'):
        transaction_count = WalletTransaction.objects.filter(wallet=user.wallet).count()

    # 2. Pending Requests/Offers Count
    pending_count = 0
    if user.type == 'B':
        # Count Pending Loan Requests
        pending_count = LoanRequest.objects.filter(borrower=user, status='PENDING').count()
    elif user.type == 'L':
        # Count Pending Offers Sent
        pending_count = LoanOffer.objects.filter(lender=user, status='PENDING').count()

    # 3. Active Loans/Investments Count
    active_count = 0
    if user.type == 'B':
        active_count = ActiveLoan.objects.filter(borrower=user, status='ACTIVE').count()
    elif user.type == 'L':
        active_count = ActiveLoan.objects.filter(lender=user, status='ACTIVE').count()

    context = {
        'user': user,
        'transaction_count': transaction_count,
        'pending_count': pending_count,
        'active_count': active_count
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

    context = {
        'user': user,
        'avg_rating': avg_rating,
        'review_count': review_count,
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

    context = {
        'profile_user': target_user,  # The user being viewed
        'avg_rating': avg_rating,
        'review_count': review_count,
        'reviews': reviews_received,
        'open_requests': open_requests,
        'viewer_id': viewer_id
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
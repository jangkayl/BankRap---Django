from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.db.models import Q, Avg
from django.db import connection
from .models import User, BorrowerProfile, LenderProfile
from loan.models import LoanOffer, LoanRequest, ActiveLoan
from review.models import ReviewAndRating
from wallet.models import WalletTransaction


def dict_fetch_one(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    return None

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


def dashboard_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    # --- Fetch Counts for Dashboard Stats ---
    transaction_count = 0
    if hasattr(user, 'wallet'):
        transaction_count =     WalletTransaction.objects.filter(wallet=user.wallet).count()

    pending_count = 0
    if user.type == 'B':
        pending_count = LoanRequest.objects.filter(borrower=user, status='PENDING').count()
    elif user.type == 'L':
        pending_count = LoanOffer.objects.filter(lender=user, status='PENDING').count()


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
        #UPDATE PROFILE
        try:

            name = request.POST.get('name')
            address = request.POST.get('address')
            contact_number = request.POST.get('contact_number')
            email = request.POST.get('email')


            income = request.POST.get('income', '0.00')
            employment_status = request.POST.get('employment_status', '')
            min_investment_amount = request.POST.get('min_investment_amount', '0.00')
            investment_preference = request.POST.get('investment_preference', '')

            with connection.cursor() as cursor:

                cursor.execute("CALL update_user_profile(%s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                    user.user_id, name, address, contact_number, email,
                    income, employment_status, min_investment_amount, investment_preference
                ])


            messages.success(request, "Profile updated successfully!")
            return redirect('profile')

        except Exception as e:
            messages.error(request, f"Error updating profile: {e}")


    try:
        with connection.cursor() as cursor:

            cursor.execute("CALL get_user_profile(%s)", [user.user_id])
            profile_data = dict_fetch_one(cursor)

        if profile_data:

            user.name = profile_data.get('name', user.name)
            user.address = profile_data.get('address', user.address)
            user.contact_number = profile_data.get('contact_number', user.contact_number)
            user.email = profile_data.get('email', user.email)


            if user.type == 'B':
                user.income = profile_data.get('income', user.income)
                user.employment_status = profile_data.get('employment_status', user.employment_status)
            elif user.type == 'L':
                user.min_investment_amount = profile_data.get('min_investment_amount', user.min_investment_amount)
                user.investment_preference = profile_data.get('investment_preference', user.investment_preference)

    except Exception as e:
        messages.warning(request, f"Error fetching profile data via SP: {e}")



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
    viewer_id = request.session.get('user_id')
    if not viewer_id:
        return redirect('login')


    target_user = get_object_or_404(User, pk=user_id)


    reviews_received = ReviewAndRating.objects.filter(reviewee=target_user).order_by('-review_date')
    avg_rating = reviews_received.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = 0.0
    review_count = reviews_received.count()


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
            # LOGIN
            user_id = None
            with connection.cursor() as cursor:
                cursor.execute("CALL authenticate_user(%s, %s, @p_out_user_id)", [identity, password])
                cursor.execute("SELECT @p_out_user_id")
                row = cursor.fetchone()
                user_id = row[0] if row else None

            if user_id:
                user = User.objects.get(user_id=user_id)
                request.session['user_id'] = user.user_id
                messages.success(request, f"Welcome back, {user.name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials.")

        except User.DoesNotExist:
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

        school_id_file_path = school_id_file.name if school_id_file else None


        if User.objects.filter(Q(email=email) | Q(student_id=student_id)).exists():
            messages.error(request, "Email or Student ID already registered.")
            return render(request, 'register.html')

        try:

            new_user_id = None
            with connection.cursor() as cursor:

                cursor.execute("CALL create_user_and_wallet(%s, %s, %s, %s, %s, %s, %s, %s, @p_out_user_id)",
                               [name, student_id, email, password, address, contact, role, school_id_file_path])

                cursor.execute("SELECT @p_out_user_id")
                row = cursor.fetchone()
                new_user_id = row[0] if row else None

            if new_user_id:

                user = User.objects.get(user_id=new_user_id)
                request.session['user_id'] = user.user_id
                messages.success(request, "Account created successfully!")
                return redirect('login')
            else:
                messages.error(request, "Registration failed: Database error.")

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

        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        password_changed = False
        email_changed = False

        try:

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


            new_email = request.POST.get('new_email')
            if new_email and new_email != user.email:

                if User.objects.filter(email=new_email).exclude(user_id=user.user_id).exists():
                    messages.error(request, "This email address is already in use.")
                else:
                    user.email = new_email
                    email_changed = True

            if password_changed or email_changed:
                user.save()
                if password_changed:
                    messages.success(request, "Password updated successfully.")
                if email_changed:
                    messages.success(request, "Email updated successfully.")
            elif not current_password and not (new_email and new_email != user.email):
                # No relevant fields filled for password/email change
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
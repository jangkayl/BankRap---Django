from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.db.models import Q, Avg
from .models import User, BorrowerProfile, LenderProfile
from wallet.models import Wallet
# Import Review model to calculate score
from review.models import ReviewAndRating


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
    return render(request, 'account/dashboard.html', {'user': user})


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

    # --- Trust Score Calculation ---
    # Fetch all reviews where this user is the 'reviewee'
    reviews_received = ReviewAndRating.objects.filter(reviewee=user)

    # Calculate average rating
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
        messages.success(request, "Settings updated successfully!")
        return redirect('settings')
    return render(request, 'account/settings.html', {'user': user})


def notifications_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    return render(request, 'account/notifications.html', {'user': user})
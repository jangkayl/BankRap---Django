from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import User, BorrowerProfile, LenderProfile
from wallet.models import Wallet


# --- Helper Function ---
def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            # First, try to get the base user
            user = User.objects.get(user_id=user_id)

            # Now try to "downcast" to the specific profile to get extra fields
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

    # Mock user for dashboard if not logged in (For UI Testing)
    if not user:
        class MockUser:
            name = "Developer Mode"

            class MockWallet:
                balance = 25000.00

            wallet = MockWallet()

        user = MockUser()

    return render(request, 'account/dashboard.html', {'user': user})


def profile_view(request):
    user = get_current_user(request)

    # Mock for UI testing if not logged in
    if not user:
        class MockUser:
            user_id = 202100123
            name = "Juan Dela Cruz"
            type = 'B'
            income = 15000.00
            credit_score = 720
            employment_status = "Part-time Student Assistant"
            available_funds = 10000.00
            min_investment_amount = 500.00

        user = MockUser()

    return render(request, 'account/profile.html', {'user': user})


def login_view(request):
    if request.method == 'POST':
        identity = request.POST.get('identity')
        password = request.POST.get('password')

        try:
            # Simple password check for prototype
            user = User.objects.get(email=identity, password=password)
            request.session['user_id'] = user.user_id
            return redirect('dashboard')

        except User.DoesNotExist:
            messages.error(request, "Invalid credentials.")

    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address', 'Cebu City')
        contact = request.POST.get('contact_number', '')
        roles = request.POST.getlist('roles')

        try:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return render(request, 'register.html')

            new_user = None

            # Create specific profile
            if 'L' in roles:
                new_user = LenderProfile.objects.create(
                    name=name, email=email, password=password,
                    address=address, contact_number=contact, type='L'
                )
            else:
                new_user = BorrowerProfile.objects.create(
                    name=name, email=email, password=password,
                    address=address, contact_number=contact, type='B'
                )

            # Create Wallet
            Wallet.objects.create(user=new_user, balance=0.00)

            messages.success(request, "Account created! Please log in.")
            return redirect('login')

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'register.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


# Keep class based view if needed for legacy/admin
class AccountView(View):
    template_name = 'account.html'

    def get(self, request):
        accounts = User.objects.all()
        return render(request, self.template_name, {'accounts': accounts})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from account.models import User, BorrowerProfile, LenderProfile
from wallet.models import Wallet  # Import Wallet model
from .models import LoanRequest, LoanOffer


# --- Helper ---
def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = User.objects.get(user_id=user_id)
            if user.type == 'B':
                return BorrowerProfile.objects.get(user_id=user_id)
            elif user.type == 'L':
                return LenderProfile.objects.get(user_id=user_id)
            return user
        except Exception:
            return None
    return None


# --- Marketplace Views (Lender Focused) ---

def loan_marketplace(request):
    """
    Main entry point for 'Loans'.
    - Lenders see the Marketplace (List of requests).
    - Borrowers are redirected to 'My Requests'.
    """
    user = get_current_user(request)
    if not user: return redirect('login')

    # 1. Strict Separation Logic
    if user.type == 'B':
        return redirect('my_loan_requests')

    # 2. Lender View: Show all PENDING requests
    loans = LoanRequest.objects.filter(status='PENDING').order_by('-request_date')

    # 3. Fetch Wallet for Available Funds Display
    wallet = None
    if user.type == 'L':
        # Use get_or_create to be safe, though register handles creation
        wallet, _ = Wallet.objects.get_or_create(user=user)

    return render(request, 'loan/marketplace.html', {
        'loans': loans,
        'user': user,
        'wallet': wallet  # Pass wallet to template
    })


def loan_detail(request, loan_id):
    """
    Detailed view of a loan.
    - Lenders see 'Make Offer'.
    - Borrowers see 'View Offers' (if it's theirs).
    """
    user = get_current_user(request)
    if not user: return redirect('login')

    loan = get_object_or_404(LoanRequest, pk=loan_id)

    # Check for existing offer from this lender
    existing_offer = None
    if user.type == 'L':
        existing_offer = LoanOffer.objects.filter(loan_request=loan, lender=user).first()

    return render(request, 'loan/loan_detail.html', {
        'loan': loan,
        'user': user,
        'existing_offer': existing_offer
    })


# --- Borrower Views ---

def my_loan_requests(request):
    """
    Borrower's dashboard for their own requests.
    """
    user = get_current_user(request)
    if not user: return redirect('login')

    if user.type == 'L':
        return redirect('loan_marketplace')

    # Show ONLY this user's requests
    my_loans = LoanRequest.objects.filter(borrower=user).order_by('-request_date')

    return render(request, 'loan/my_requests.html', {
        'loans': my_loans,
        'user': user
    })


def create_loan_request(request):
    # Mapping for urls.py which might call 'loan_request_create'
    return loan_request_create(request)


def loan_request_create(request):
    user = get_current_user(request)
    if not user: return redirect('login')

    if user.type != 'B':
        messages.error(request, "Only borrowers can create loan requests.")
        return redirect('loan_marketplace')

    if request.method == 'POST':
        try:
            LoanRequest.objects.create(
                borrower=user,
                amount=request.POST.get('amount'),
                interest_rate=request.POST.get('interest_rate'),
                term=request.POST.get('term'),
                purpose=request.POST.get('purpose'),
                status='PENDING'
            )
            messages.success(request, "Loan request posted successfully!")
            return redirect('my_loan_requests')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'loan/request_create.html', {'user': user})


# --- Offer Logic ---

def create_offer(request, loan_id):
    user = get_current_user(request)
    if not user or user.type != 'L': return redirect('login')

    loan = get_object_or_404(LoanRequest, pk=loan_id)

    if request.method == 'POST':
        LoanOffer.objects.create(
            loan_request=loan,
            lender=user,
            offered_amount=request.POST.get('amount'),
            offered_rate=request.POST.get('interest_rate'),
            message=request.POST.get('message'),
            status='PENDING'
        )
        messages.success(request, "Offer sent!")
        return redirect('loan_marketplace')

    return render(request, 'loan/offer_create.html', {'loan': loan, 'user': user})


# Stub functions to satisfy urls.py imports if they exist there
def loan_request_list(request): return loan_marketplace(request)


def loan_offer_create(request, loan_id): return create_offer(request, loan_id)


def loan_offer_list(request): return offer_list(request)


def offer_list(request):
    user = get_current_user(request)
    if not user: return redirect('login')
    offers = LoanOffer.objects.all()
    return render(request, 'loan/offer_list.html', {'offers': offers, 'user': user})


def repayment_schedule(request):
    user = get_current_user(request)
    return render(request, 'loan/repayment_schedule.html', {'user': user})
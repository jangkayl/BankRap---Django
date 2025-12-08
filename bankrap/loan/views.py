from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.utils import OperationalError, ProgrammingError
from account.models import User, BorrowerProfile, LenderProfile
from .models import LoanRequest, LoanOffer
from django.shortcuts import get_object_or_404


# ==========================================
# VIEW 1: List All Loan Requests
# ==========================================
def loan_request_list(request):
    loans = []
    try:
        loans = LoanRequest.objects.all().order_by('-request_date')
    except (OperationalError, ProgrammingError):
        loans = []

    # --- MOCK DATA (Loads if DB is empty) ---
    if not loans:
        class MockLoan:
            def __init__(self, id, amount, interest, term_val, term_unit, status):
                self.loan_id = id
                self.amount = amount
                self.interest_rate = interest
                self.term_value = term_val
                self.term_unit = 'MONTHS'
                self.status = status

            def get_term_unit_display(self):
                return "Months"

        loans = [
            MockLoan(1, 15000, 5, 3, 'MONTHS', 'APPROVED'),
            MockLoan(2, 20000, 6, 6, 'MONTHS', 'PENDING'),
            MockLoan(3, 10000, 4.5, 2, 'MONTHS', 'REPAID'),
            MockLoan(4, 25000, 5.5, 9, 'MONTHS', 'REJECTED'),
            MockLoan(5, 18000, 5.2, 4, 'MONTHS', 'APPROVED'),
            MockLoan(6, 12000, 4.8, 3, 'MONTHS', 'PENDING'),
        ]

    return render(request, 'loan/request_list.html', {'loans': loans})


# ==========================================
# VIEW 2: Create New Loan Request
# ==========================================
def loan_request_create(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "You must be logged in.")
            return redirect('login')

        try:
            try:
                borrower = BorrowerProfile.objects.get(user_id=user_id)
            except BorrowerProfile.DoesNotExist:
                user = User.objects.get(user_id=user_id)
                borrower = user

            amount = request.POST.get('amount')
            interest = request.POST.get('interest_rate')
            purpose = request.POST.get('purpose')
            term_raw = request.POST.get('term')

            if term_raw:
                term_val, term_unit = term_raw.split('_')
            else:
                term_val, term_unit = 1, 'MONTHS'

            LoanRequest.objects.create(
                borrower_profile=borrower,
                amount=amount,
                interest_rate=interest,
                purpose=purpose,
                term_value=term_val,
                term_unit=term_unit,
                status='PENDING'
            )

            messages.success(request, "Loan request submitted successfully!")
            return redirect('loan_list')

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('loan_list')

    return render(request, 'loan/request_create.html')


# ==========================================
# VIEW 3: Create Loan Offer
# ==========================================
def loan_offer_create(request, loan_id):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Please log in.")
            return redirect('login')

        try:
            loan_request_obj = LoanRequest.objects.get(loan_id=loan_id)

            try:
                lender = LenderProfile.objects.get(user_id=user_id)
            except LenderProfile.DoesNotExist:
                lender = User.objects.get(user_id=user_id)

            amount = request.POST.get('amount')
            rate = request.POST.get('interest_rate')

            LoanOffer.objects.create(
                loan_request=loan_request_obj,
                lender_profile=lender,
                offered_amount=amount,
                offered_rate=rate,
                offer_status='PENDING'
            )

            messages.success(request, "Loan offer sent successfully!")
            return redirect('loan_list')

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('loan_list')

    return render(request, 'loan/offer_create.html')


# ==========================================
# VIEW 4: List Loan Offers
# ==========================================
def loan_offer_list(request):
    offers = []

    # Try to fetch real data
    try:
        offers = LoanOffer.objects.all().order_by('-offer_date')
    except (OperationalError, ProgrammingError):
        offers = []

    # --- MOCK DATA (If DB is empty) ---
    if not offers:
        from datetime import datetime
        class MockReq:
            loan_id = 101

        class MockOffer:
            def __init__(self, amount, rate, status, date_str):
                self.loan_request = MockReq()
                self.offered_amount = amount
                self.offered_rate = rate
                self.offer_status = status
                self.offer_date = datetime.strptime(date_str, "%Y-%m-%d")

        offers = [
            MockOffer(5000, 5.0, 'ACCEPTED', '2025-11-20'),
            MockOffer(3000, 6.5, 'PENDING', '2025-12-01'),
            MockOffer(10000, 4.0, 'DECLINED', '2025-10-15'),
        ]

    return render(request, 'loan/offer_list.html', {'offers': offers})


# ==========================================
# VIEW 5: Loan Detail Page
# ==========================================
def loan_detail(request, loan_id):
    loan = None
    try:
        # Try to get real object
        loan = get_object_or_404(LoanRequest, loan_id=loan_id)
    except Exception:
        # Fallback Mock Object for UI Dev if DB is empty/broken
        from datetime import datetime
        class MockUser:
            name = "Alodia Gosiengfiao"

        class MockLoan:
            def __init__(self, id):
                self.loan_id = id
                self.amount = 2500.00
                self.interest_rate = 5
                self.term_value = 6
                self.term_unit = 'MONTHS'
                self.status = 'APPROVED'
                self.purpose = "Tuition Fee"
                self.request_date = datetime.now()
                self.borrower_profile = MockUser()

            def get_term_unit_display(self):
                return "Months"

        loan = MockLoan(loan_id)

    return render(request, 'loan/loan_detail.html', {'loan': loan})
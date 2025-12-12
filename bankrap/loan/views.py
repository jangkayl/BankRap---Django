from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from account.models import User, BorrowerProfile, LenderProfile
from wallet.models import Wallet, WalletTransaction
from transaction.models import Transaction
from .models import LoanRequest, LoanOffer, ActiveLoan


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


# --- Marketplace Views ---

def loan_marketplace(request):
    user = get_current_user(request)
    if not user: return redirect('login')
    if user.type == 'B': return redirect('my_loan_requests')

    loans = LoanRequest.objects.filter(status='PENDING').order_by('-request_date')

    wallet = None
    if user.type == 'L':
        wallet, _ = Wallet.objects.get_or_create(user=user)

    return render(request, 'loan/marketplace.html', {
        'loans': loans,
        'user': user,
        'wallet': wallet
    })


def loan_detail(request, loan_id):
    user = get_current_user(request)
    if not user: return redirect('login')

    loan = get_object_or_404(LoanRequest, pk=loan_id)

    existing_offer = None
    offer_history = None
    received_offers = None
    loan_transactions = None

    if user.type == 'L':
        offer_history = LoanOffer.objects.filter(loan_request=loan, lender=user).order_by('-offer_date')
        existing_offer = offer_history.exclude(status='DECLINED').exclude(status='CANCELLED').first()

    elif user.type == 'B':
        received_offers = LoanOffer.objects.filter(loan_request=loan).order_by('-offer_date')

    loan_transactions = Transaction.objects.filter(loan_request=loan).order_by('-transaction_date')

    return render(request, 'loan/loan_detail.html', {
        'loan': loan,
        'user': user,
        'existing_offer': existing_offer,
        'offer_history': offer_history,
        'received_offers': received_offers,
        'loan_transactions': loan_transactions
    })


# --- Borrower Views ---

def my_loan_requests(request):
    user = get_current_user(request)
    if not user: return redirect('login')
    if user.type == 'L': return redirect('loan_marketplace')

    my_loans = LoanRequest.objects.filter(borrower=user).order_by('-request_date')
    return render(request, 'loan/my_requests.html', {'loans': my_loans, 'user': user})


def create_loan_request(request): return loan_request_create(request)


def loan_request_create(request):
    user = get_current_user(request)
    if not user: return redirect('login')
    if user.type != 'B': return redirect('loan_marketplace')

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


# --- Offer Logic (UPDATED WITH FUND HOLDING) ---

def create_offer(request, loan_id):
    user = get_current_user(request)
    if not user or user.type != 'L': return redirect('login')

    loan = get_object_or_404(LoanRequest, pk=loan_id)

    if request.method == 'POST':
        try:
            # FIX: Convert to Decimal instead of float
            amount = Decimal(request.POST.get('amount'))

            with db_transaction.atomic():
                # 1. Get Lender Wallet (Lock row)
                wallet = Wallet.objects.select_for_update().get(user=user)

                # 2. Check Balance
                if wallet.balance < amount:
                    messages.error(request, "Insufficient funds to make this offer.")
                    return redirect('loan_detail', loan_id=loan.loan_id)

                # 3. Deduct/Hold Funds
                wallet.withdraw(amount)

                # 4. Create Wallet Transaction (Escrow/Hold)
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type="WITHDRAW",
                    reference_number=f"HOLD-OFFER-{loan.loan_id}"
                )

                # 5. Create Offer
                LoanOffer.objects.create(
                    loan_request=loan,
                    lender=user,
                    offered_amount=amount,
                    offered_rate=request.POST.get('interest_rate'),
                    message=request.POST.get('message'),
                    status='PENDING'
                )

            messages.success(request, f"Offer sent! ₱{amount} has been held from your wallet.")
            return redirect('loan_marketplace')

        except Exception as e:
            # Add specific error message for debugging if needed, but generic is fine for users
            messages.error(request, f"Error processing offer: {e}")
            return redirect('loan_detail', loan_id=loan.loan_id)

    return render(request, 'loan/offer_create.html', {'loan': loan, 'user': user})

# --- ACCEPT / DECLINE LOGIC (UPDATED) ---

def accept_offer(request, offer_id):
    user = get_current_user(request)
    if not user or user.type != 'B': return redirect('login')

    offer = get_object_or_404(LoanOffer, pk=offer_id)

    if offer.loan_request.borrower.user_id != user.user_id:
        return redirect('my_loan_requests')
    if offer.status != 'PENDING':
        messages.error(request, "This offer is no longer valid.")
        return redirect('my_loan_requests')

    try:
        with db_transaction.atomic():
            # Funds are ALREADY deducted from lender (held).
            # We just need to credit borrower and refund OTHER lenders.

            # 1. Credit Borrower
            borrower_wallet = Wallet.objects.select_for_update().get(user=user)
            borrower_wallet.deposit(offer.offered_amount)

            # 2. Record Borrower Deposit
            WalletTransaction.objects.create(
                wallet=borrower_wallet,
                amount=offer.offered_amount,
                transaction_type="DEPOSIT",
                reference_number=f"LOAN-RECEIVED-{offer.loan_request.loan_id}"
            )

            # 3. Record Loan History Transaction (Disbursement)
            Transaction.objects.create(
                loan_request=offer.loan_request,
                user=offer.lender,
                amount=offer.offered_amount,
                transaction_data=f"Disbursement to {user.name}",
                type='D',
                status='C',
                reference_number=f"LOAN-{offer.loan_request.loan_id}-DISB"
            )

            # 4. Update Main Offer & Request
            offer.status = 'ACCEPTED'
            offer.save()
            offer.loan_request.status = 'FUNDED'
            offer.loan_request.save()

            # 5. Create Active Loan
            days = 30
            if 'DAYS' in offer.loan_request.term:
                try:
                    days = int(offer.loan_request.term.split('_')[0])
                except:
                    days = 30
            else:
                try:
                    days = int(offer.loan_request.term.split('_')[0]) * 30
                except:
                    days = 30

            due_date = timezone.now().date() + timedelta(days=days)
            total_repay = offer.offered_amount * (1 + (offer.offered_rate / 100))

            ActiveLoan.objects.create(
                loan_request=offer.loan_request,
                lender=offer.lender,
                borrower=user,
                principal_amount=offer.offered_amount,
                interest_rate=offer.offered_rate,
                total_repayment=total_repay,
                due_date=due_date
            )

            # 6. REFUND OTHER PENDING OFFERS
            # Since we held funds for ALL pending offers, we must refund the losers.
            other_offers = LoanOffer.objects.filter(loan_request=offer.loan_request, status='PENDING').exclude(
                pk=offer.offer_id)

            for other in other_offers:
                # Refund logic
                lender_refund_wallet = Wallet.objects.select_for_update().get(user=other.lender)
                lender_refund_wallet.deposit(other.offered_amount)

                # Record Refund
                WalletTransaction.objects.create(
                    wallet=lender_refund_wallet,
                    amount=other.offered_amount,
                    transaction_type="DEPOSIT",
                    reference_number=f"REFUND-OFFER-{other.offer_id}"
                )

                other.status = 'DECLINED'
                other.save()

            messages.success(request, f"Offer accepted! ₱{offer.offered_amount} added to wallet.")
            return redirect('wallet')

    except Exception as e:
        messages.error(request, f"Transaction failed: {e}")
        return redirect('my_loan_requests')


def decline_offer(request, offer_id):
    user = get_current_user(request)
    if not user or user.type != 'B': return redirect('login')

    offer = get_object_or_404(LoanOffer, pk=offer_id)

    if offer.loan_request.borrower.user_id != user.user_id:
        return redirect('my_loan_requests')

    if offer.status != 'PENDING':
        messages.error(request, "Cannot decline non-pending offer.")
        return redirect('loan_detail', loan_id=offer.loan_request.loan_id)

    try:
        with db_transaction.atomic():
            # 1. Refund Lender
            lender_wallet = Wallet.objects.select_for_update().get(user=offer.lender)
            lender_wallet.deposit(offer.offered_amount)

            # 2. Record Refund
            WalletTransaction.objects.create(
                wallet=lender_wallet,
                amount=offer.offered_amount,
                transaction_type="DEPOSIT",
                reference_number=f"REFUND-DECLINED-{offer.offer_id}"
            )

            # 3. Update Status
            offer.status = 'DECLINED'
            offer.save()

            messages.info(request, "Offer declined and funds refunded to lender.")
            return redirect('loan_detail', loan_id=offer.loan_request.loan_id)

    except Exception as e:
        messages.error(request, f"Error declining offer: {e}")
        return redirect('loan_detail', loan_id=offer.loan_request.loan_id)


# --- Stubs & Lists ---
def loan_request_list(request): return loan_marketplace(request)


def loan_offer_create(request, loan_id): return create_offer(request, loan_id)


def loan_offer_list(request): return offer_list(request)


def offer_list(request):
    user = get_current_user(request)
    if not user: return redirect('login')

    offers = []
    if user.type == 'B':
        offers = LoanOffer.objects.filter(loan_request__borrower=user).order_by('-offer_date')
    elif user.type == 'L':
        offers = LoanOffer.objects.filter(lender=user).order_by('-offer_date')

    return render(request, 'loan/offer_list.html', {'offers': offers, 'user': user})


def repayment_schedule(request):
    user = get_current_user(request)
    if not user: return redirect('login')

    active_loans = []
    if user.type == 'B':
        active_loans = ActiveLoan.objects.filter(borrower=user).order_by('due_date')
    elif user.type == 'L':
        active_loans = ActiveLoan.objects.filter(lender=user).order_by('due_date')

    return render(request, 'loan/repayment_schedule.html', {'user': user, 'active_loans': active_loans})
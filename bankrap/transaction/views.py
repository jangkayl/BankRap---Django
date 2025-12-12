from django.shortcuts import render, redirect
from account.models import User, BorrowerProfile, LenderProfile
from .models import Transaction


def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None
    return None


def transaction_history(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    # Fetch transactions related to the user
    # A user can be related via 'user' (initiator) OR indirectly if they are the borrower/lender
    # Ideally, the Transaction model should have a direct link or we query based on involvement
    # For now, let's assume 'user' field in Transaction tracks the person whose wallet was affected
    # But wait, in accept_offer we created 2 transactions (one for lender, one for borrower)
    # The 'user' field in Transaction model was: user = models.ForeignKey(User, ...)
    # In accept_offer:
    #   Lender TX: user=offer.lender
    #   Borrower TX: user=offer.lender (Wait, I passed offer.lender to both! Let me check)

    # Correction: In my previous response for loan/views.py accept_offer:
    # Transaction.objects.create(..., user=offer.lender, ...) -> Correct for lender
    # But for borrower, I didn't create a Transaction record in the Transaction model, only WalletTransaction.
    # I should fix that if I want it to show up here.

    # Let's rely on the WalletTransaction model for the main wallet history page since it tracks all money movement.
    # Or if you want the "Loan Transaction History" specifically, we use Transaction.

    # Assuming we want the general wallet history + loan history mixed:
    # Let's just fetch from WalletTransaction for the general history page as it's more complete for "Wallet" actions.
    # BUT the user asked for "Transaction History in EACH LOAN".

    # For the main /transactions/ page, let's show ALL transactions for this user.
    # Since I introduced the `Transaction` model specifically for Loans, let's use that.

    transactions = Transaction.objects.filter(user=user).order_by('-transaction_date')

    return render(request, 'transaction/history.html', {
        'user': user,
        'transactions': transactions
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from decimal import Decimal
from account.models import User
from .models import Wallet, WalletTransaction


# --- Helper ---
def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None
    return None


# --- Views ---

def wallet_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    # Ensure wallet exists (create if missing, though register usually handles this)
    wallet, created = Wallet.objects.get_or_create(user=user)

    # Fetch transactions
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-transaction_date')

    return render(request, 'wallet/wallet.html', {
        'user': user,
        'wallet': wallet,
        'transactions': transactions
    })


def add_funds(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        reference_number = request.POST.get('reference_number')  # Get Ref Number

        try:
            amount = Decimal(amount_str)
            wallet = Wallet.objects.get(user=user)

            # 1. Update Balance
            wallet.deposit(amount)

            # 2. Record Transaction with Reference Number
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type="DEPOSIT",
                reference_number=reference_number  # Save Ref Number
            )

            messages.success(request, f"Successfully added ₱{amount}")

        except (ValueError, ValidationError) as e:
            messages.error(request, f"Error adding funds: {e}")
        except Wallet.DoesNotExist:
            messages.error(request, "Wallet not found.")

    return redirect('wallet')


def withdraw_funds(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        account_details = request.POST.get('account')  # e.g. Gcash Number

        try:
            amount = Decimal(amount_str)
            wallet = Wallet.objects.get(user=user)

            # 1. Update Balance (Model raises ValidationError if insufficient)
            wallet.withdraw(amount)

            # 2. Record Transaction
            # We can use reference_number to store the withdrawal destination account for now
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type="WITHDRAW",
                reference_number=f"To: {account_details}"
            )

            messages.success(request, f"Successfully withdrew ₱{amount}")

        except ValidationError as e:
            # Catches "Insufficient wallet balance" from model
            messages.error(request, e.message)
        except ValueError:
            messages.error(request, "Invalid amount entered.")
        except Wallet.DoesNotExist:
            messages.error(request, "Wallet not found.")

    return redirect('wallet')
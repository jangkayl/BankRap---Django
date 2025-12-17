from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import connection
from django.utils import timezone
from decimal import Decimal
from account.models import User
from .models import Wallet, WalletTransaction


def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None
    return None


def wallet_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    wallet, created = Wallet.objects.get_or_create(user=user)
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
        reference_number = request.POST.get('reference_number')

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValidationError("Amount must be positive.")

            current_time = timezone.now()

            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL sp_add_funds(%s, %s, %s, %s)",
                    [user.user_id, amount, reference_number, current_time]
                )

            messages.success(request, f"Successfully added ₱{amount}")

        except (ValueError, ValidationError) as e:
            messages.error(request, f"Error adding funds: {e}")
        except Exception as e:
            messages.error(request, f"Database error: {e}")

    return redirect('wallet')


def withdraw_funds(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        account_details = request.POST.get('account')

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValidationError("Amount must be positive.")

            current_time = timezone.now()

            with connection.cursor() as cursor:
                cursor.execute(
                    "CALL sp_withdraw_funds(%s, %s, %s, %s, @status, @message)",
                    [user.user_id, amount, account_details, current_time]
                )

                cursor.execute("SELECT @status, @message")
                result = cursor.fetchone()

                status = result[0]
                message = result[1]

            if status == 'SUCCESS':
                messages.success(request, f"Successfully withdrew ₱{amount}")
            else:
                messages.error(request, message)

        except (ValueError, ValidationError) as e:
            messages.error(request, f"Invalid input: {e}")
        except Exception as e:
            messages.error(request, f"System error: {e}")

    return redirect('wallet')
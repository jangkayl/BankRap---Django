from django.shortcuts import render, redirect
from account.models import User
from .models import Wallet, WalletTransaction


def wallet_view(request):
    user_id = request.session.get('user_id')

    # Mock user if not logged in (For UI dev)
    if not user_id:
        class MockUser:
            name = "Developer Mode"

            class MockWallet:
                balance = 2850.75

            wallet = MockWallet()

        user = MockUser()
        transactions = []
    else:
        try:
            user = User.objects.get(user_id=user_id)
            # Fetch real transactions if they exist
            if hasattr(user, 'wallet'):
                transactions = WalletTransaction.objects.filter(wallet=user.wallet).order_by('-transaction_date')
            else:
                transactions = []
        except User.DoesNotExist:
            return redirect('login')

    return render(request, 'wallet/wallet.html', {
        'user': user,
        'transactions': transactions
    })


# Placeholder for form action
def add_funds(request):
    # Logic to add funds would go here
    return redirect('wallet')
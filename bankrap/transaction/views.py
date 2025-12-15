from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from account.models import User
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

    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    type_filter = request.GET.get('type', 'all')
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)

    # Base query
    transactions = Transaction.objects.filter(user=user)

    # Apply filters
    if status_filter != 'all':
        if status_filter == 'completed':
            transactions = transactions.filter(status='C')
        elif status_filter == 'pending':
            transactions = transactions.filter(status='P')
        elif status_filter == 'failed':
            transactions = transactions.filter(status='F')

    if type_filter != 'all':
        if type_filter == 'disbursement':
            transactions = transactions.filter(type='D')
        elif type_filter == 'repayment':
            transactions = transactions.filter(type='R')

    if search_query:
        transactions = transactions.filter(
            transaction_data__icontains=search_query
        )

    transactions = transactions.order_by('-transaction_date')

    # Pagination
    paginator = Paginator(transactions, 15)  # Show 15 transactions per page
    page_obj = paginator.get_page(page_number)

    return render(request, 'transaction/history.html', {
        'user': user,
        'transactions': page_obj,  # Changed to page_obj
        'current_status': status_filter,
        'current_type': type_filter,
        'search_query': search_query
    })
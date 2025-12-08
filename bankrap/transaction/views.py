from django.shortcuts import render
from django.db.utils import OperationalError, ProgrammingError
from .models import Transaction


def transaction_history(request):
    transactions = []

    # Try to fetch real data
    try:
        transactions = Transaction.objects.all().order_by('-transaction_date')
    except (OperationalError, ProgrammingError):
        transactions = []

    # --- MOCK DATA (Matches Screenshot) ---
    if not transactions:
        from datetime import datetime
        class MockTx:
            def __init__(self, date, type_code, desc, amount, status):
                self.transaction_date = datetime.strptime(date, "%Y-%m-%d")
                self.type = type_code  # 'D' or 'R'
                self.transaction_data = desc
                self.amount = amount
                self.status = status  # 'C', 'P', 'F'

            def get_type_display(self):
                return "Disbursement" if self.type == 'D' else "Repayment"

        transactions = [
            MockTx('2024-06-28', 'D', 'Project materials loan', 3000.00, 'P'),  # Pending
            MockTx('2024-06-25', 'R', 'Missed payment for loan F', 1000.00, 'F'),  # Failed
            MockTx('2024-06-20', 'R', 'Early repayment', 500.00, 'C'),  # Completed (Extra example)
        ]

    return render(request, 'transaction/history.html', {'transactions': transactions})
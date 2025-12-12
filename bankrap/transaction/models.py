from django.db import models
from account.models import User
from loan.models import LoanRequest


class Transaction(models.Model):
    TYPE_CHOICES = (
        ('D', 'Disbursement'),
        ('R', 'Repayment')
    )
    STATUS_CHOICES = (
        ('C', 'Completed'),
        ('P', 'Pending'),
        ('F', 'Failed')
    )

    transaction_id = models.AutoField(primary_key=True)

    # Link to the specific loan this transaction belongs to
    loan_request = models.ForeignKey(LoanRequest, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='loan_transactions')

    # The user who initiated or is the primary actor (e.g., Lender for disbursement, Borrower for repayment)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_transactions')

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    transaction_data = models.CharField(max_length=255)  # Description
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='D')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Transactions"
        ordering = ['-transaction_date']

    def __str__(self):
        return f"TX {self.transaction_id}: {self.get_type_display()} - {self.amount}"
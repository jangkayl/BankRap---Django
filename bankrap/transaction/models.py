from django.db import models

from account.models import LenderProfile
from loan.models import LoanRequest

# Create your models here.
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

    loan_request = models.ForeignKey(LoanRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    lender_profile = models.ForeignKey(LenderProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='initiated_transactions')

    transaction_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    transaction_data = models.CharField(max_length=255)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='D')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"TX {self.transaction_id}: {self.type} - {self.amount}"


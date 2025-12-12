from django.db import models
from account.models import User


class LoanRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('FUNDED', 'Funded'),
        ('REPAID', 'Repaid'),
        ('REJECTED', 'Rejected'),
    )

    TERM_CHOICES = (
        ('7_DAYS', '7 Days'),
        ('15_DAYS', '15 Days'),
        ('1_MONTH', '1 Month'),
        ('2_MONTHS', '2 Months'),
        ('3_MONTHS', '3 Months'),
        ('4_MONTHS', '4 Months'),
        ('5_MONTHS', '5 Months'),
        ('6_MONTHS', '6 Months'),
        ('12_MONTHS', '12 Months'),
    )

    loan_id = models.AutoField(primary_key=True)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_requests')

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.loan_id} by {self.borrower.name}"

    @property
    def term_value(self):
        try:
            return int(self.term.split('_')[0])
        except:
            return 0

    @property
    def get_term_unit_display(self):
        return "Months"


class LoanOffer(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    )

    offer_id = models.AutoField(primary_key=True)
    loan_request = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='offers')
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_offers')

    offered_amount = models.DecimalField(max_digits=12, decimal_places=2)
    offered_rate = models.DecimalField(max_digits=5, decimal_places=2)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    offer_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer by {self.lender.name} for Request #{self.loan_request.loan_id}"


class ActiveLoan(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('PAID', 'Paid'),
        ('DEFAULTED', 'Defaulted'),
    )

    active_loan_id = models.AutoField(primary_key=True)
    loan_request = models.OneToOneField(LoanRequest, on_delete=models.CASCADE, related_name='active_loan')
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liabilities')

    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    total_repayment = models.DecimalField(max_digits=12, decimal_places=2)

    start_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    def __str__(self):
        return f"Active Loan #{self.active_loan_id} ({self.borrower.name})"
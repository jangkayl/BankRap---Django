from django.db import models

from account.models import BorrowerProfile, LenderProfile

# Create your models here.
class LoanRequest(models.Model):
    LOAN_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("REPAID", "Repaid"),
    ]
    TERM_UNIT_CHOICES = [
        ("DAYS", "Days"),
        ("WEEKS", "Weeks"),
        ("MONTHS", "Months"),
    ]

    borrower_profile = models.ForeignKey(BorrowerProfile, on_delete=models.CASCADE, related_name="loan_requests")
    loan_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    purpose = models.TextField()
    status = models.CharField(max_length=10, choices=LOAN_STATUS_CHOICES, default="PENDING")
    request_date = models.DateTimeField(auto_now_add=True)
    term_value = models.PositiveIntegerField(help_text="Loan term duration (numeric value)", default=1)
    term_unit = models.CharField(max_length=10, choices=TERM_UNIT_CHOICES, default="DAYS", help_text="Loan term unit")

    def __str__(self):
        return f"LoanRequest {self.loan_id} - {self.status}"

class LoanOffer(models.Model):
    OFFER_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
    ]

    loan_request = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name="loan_offers")
    lender_profile = models.ForeignKey(LenderProfile, on_delete=models.CASCADE, related_name="loan_offers")

    offer_id = models.AutoField(primary_key=True)
    offered_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    offered_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    offer_status = models.CharField(max_length=10, choices=OFFER_STATUS_CHOICES, default="PENDING")
    offer_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"LoanOffer {self.offer_id} for LoanRequest {self.loan_request.loan_id}"

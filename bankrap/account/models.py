from django.db import models

# Create your models here.
class User(models.Model):
    USER_TYPE = (
        ('L', 'Lender'),
        ('B', 'Borrower')
    )

    user_id = models.AutoField(primary_key=True)
    student_id = models.CharField(max_length=20, unique=True, null=True)
    name = models.CharField(max_length=40)
    email = models.EmailField()
    password = models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    contact_number = models.CharField(max_length=20)
    type = models.CharField(max_length=1, choices=USER_TYPE)

    school_id_file = models.FileField(upload_to='school_ids/', blank=True, null=True)

    def __str__(self):
        return self.name

class LenderProfile(User):
    investment_preference = models.CharField(max_length=200)
    available_funds = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    min_investment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    profile_created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Lender: {self.name} | Available Funds: {str(self.available_funds)}"

class BorrowerProfile(User):
    income = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    credit_score = models.IntegerField(default=0)
    employment_status = models.CharField(max_length=50)
    profile_created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Borrower: {self.name} | Credit Score: {self.credit_score}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('LOAN_APPROVED', 'Loan Approved'),
        ('LOAN_OFFER', 'New Loan Offer'),
        ('REPAYMENT_DUE', 'Repayment Due'),
        ('VERIFICATION', 'Verification'),
        ('MESSAGE', 'New Message'),
        ('OFFER_ACCEPTED', 'Offer Accepted'),
        ('LOAN_FUNDED', 'Loan Funded'),
        ('LOAN_REJECTED', 'Loan Rejected'),
        ('REPAYMENT_MADE', 'Repayment Made'),
        ('WALLET', 'Wallet Transaction'),
    )

    PRIORITY_CHOICES = (
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    )

    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')

    # Use string references instead of importing loan models
    loan_request = models.ForeignKey('loan.LoanRequest', on_delete=models.SET_NULL, null=True, blank=True)
    loan_offer = models.ForeignKey('loan.LoanOffer', on_delete=models.SET_NULL, null=True, blank=True)
    active_loan = models.ForeignKey('loan.ActiveLoan', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]

    def __str__(self):
        return f"{self.notification_type} - {self.user.name} - {'Read' if self.is_read else 'Unread'}"

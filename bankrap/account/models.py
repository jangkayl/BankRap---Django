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
    NOTIFICATION_TYPES = [
        ('LOAN_APPROVED', 'Loan Approved'),
        ('LOAN_OFFER', 'New Loan Offer'),
        ('REPAYMENT_DUE', 'Repayment Due'),
        ('VERIFICATION', 'Verification Status'),
        ('MESSAGE', 'New Message'),
        ('OFFER_ACCEPTED', 'Offer Accepted'),
        ('LOAN_REJECTED', 'Loan Rejected'),
        ('REPAYMENT_MADE', 'Repayment Made'),
        ('WALLET', 'Wallet Transaction'),
        ('SYSTEM', 'System Notification'),
    ]

    PRIORITY_LEVELS = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='MEDIUM')

    # Add these new fields for click actions
    action_url = models.CharField(max_length=255, blank=True, null=True)
    related_id = models.IntegerField(blank=True, null=True)  # ID of related object (loan_id, offer_id, etc.)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.name}"

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')

    # Optional: Link to loan for context
    loan_request = models.ForeignKey('loan.LoanRequest', on_delete=models.SET_NULL, null=True, blank=True)

    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sender', 'receiver', 'created_at']),
        ]

    def __str__(self):
        return f"{self.sender.name} → {self.receiver.name}: {self.content[:50]}"

    def time_ago(self):
        """Human readable time difference"""
        from django.utils import timezone
        now = timezone.now()
        diff = now - self.created_at

        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
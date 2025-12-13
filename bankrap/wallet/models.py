from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from account.models import User


class Wallet(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    def deposit(self, amount):
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive.")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive.")
        if self.balance < amount:
            raise ValidationError("Insufficient wallet balance.")
        self.balance -= amount
        self.save()

    def __str__(self):
        return f"{self.user.name}'s Wallet — Balance: {self.balance}"


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("DEPOSIT", "Deposit"),
        ("WITHDRAW", "Withdrawal"),
        ("HOLD", "On Hold"),
        ("REFUND", "Returned"),
        ("LOAN_RCV", "Loan Received"),
        ("LOAN_PAY", "Loan Payment"),
        ("LOAN_REP", "Repayment Received"),
    ]

    transaction_id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} | Ref: {self.reference_number}"
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
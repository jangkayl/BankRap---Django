from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from account.models import User
from loan.models import LoanRequest

class ReviewAndRating(models.Model):
    REVIEW_TYPE_CHOICES = [
        ('B2L', 'Borrower-to-Lender'),
        ('L2B', 'Lender-to-Borrower'),
    ]

    review_id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(LoanRequest, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=0)
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)
    review_type = models.CharField(max_length=3, choices=REVIEW_TYPE_CHOICES)

    class Meta:
        # Enforce one review per loan per reviewer
        unique_together = ('loan', 'reviewer')

    def clean(self):
        if self.reviewer == self.reviewee:
            raise ValidationError("Reviewer and reviewee cannot be the same person.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reviewer.name} -> {self.reviewee.name} | {self.rating}/5"
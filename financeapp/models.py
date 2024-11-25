"""
This module defines the database models for the financeapp application.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator

class Transaction(models.Model):
    """Represents a financial transaction by a user."""
    INCOME = 'Income'
    EXPENSE = 'Expense'

    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=100)
    type = models.CharField(
        max_length=7,
        choices=TRANSACTION_TYPE_CHOICES,
    )

    def __str__(self):
        return f"{self.user} - {self.category} - {self.type} - {self.amount}"

class Budget(models.Model):
    """Represents a user's budget."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    alert_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}'s Budget: ${self.total_amount}"

# Contact model
class Contact(models.Model):
    """Represents a contact submission from a user."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField(validators=[MaxLengthValidator(1000)])
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self): # Corrected to __str__
        return f"{self.name} - {self.subject}" # Removed non-breaking space

class SavingsGoal(models.Model):
    """Represents a user's savings goal."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(decimal_places=2, max_digits=10)
    current_amount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - Target: ${self.target_amount:.2f}"

class SavingsTransaction(models.Model):
    """Represents a transaction towards a savings goal."""
    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    date = models.DateField()

    def __str__(self):
        return f"${self.amount:.2f} towards {self.goal.name} on {self.date}"

class Notification(models.Model):
    """Represents an in-app notification for a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}: {self.message}" # Corrected to access user directly

class UserImage(models.Model):
    """Represents the user to upload images"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/user_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator

class Transaction(models.Model):
    INCOME = 'Income'
    EXPENSE = 'Expense'

    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=100)
    type = models.CharField(
        max_length=7,
        choices=TRANSACTION_TYPE_CHOICES,
        
    )

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.type} - {self.amount}"

class Budget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    alert_sent = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.username}'s Budget: ${self.total_amount}"
        
# Contact model
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField(validators=[MaxLengthValidator(1000)])
    date_submitted = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.name} - {self.subject}"

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(decimal_places=2, max_digits=10)
    current_amount = models.DecimalField(decimal_places=2, max_digits=10, default=0) 
    deadline = models.DateField(null=True, blank=True) 

    def __str__(self):
        return f"{self.name} - Target: ${self.target_amount:.2f}"

class SavingsTransaction(models.Model):
    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    date = models.DateField()

    def __str__(self):
        return f"${self.amount:.2f} towards {self.goal.name} on {self.date}"
        
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255) 
    link = models.CharField(max_length=255, blank=True, null=True)  # Optional link
    is_read = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
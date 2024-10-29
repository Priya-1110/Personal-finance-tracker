from django.db import models
from django.contrib.auth.models import User

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

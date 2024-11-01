"""
This module registers models with the Django admin site
"""
from django.contrib import admin
from .models import Transaction, Budget, Contact, SavingsGoal, SavingsTransaction, Notification
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(SavingsGoal)
admin.site.register(SavingsTransaction)
admin.site.register(Contact)
admin.site.register(Notification)

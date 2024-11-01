"""This module contains the forms for the finance app."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction, Budget, SavingsGoal, SavingsTransaction

class UserRegisterForm(UserCreationForm): # pylint: disable=too-many-ancestors
    """
    Custom form for user registration
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:# pylint: disable=too-few-public-methods
        """
        meta class
        """
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class IncomeForm(forms.ModelForm):
    """
    Form for adding income transactions
    """
    class Meta:# pylint: disable=too-few-public-methods
        """
        meta class
        """
        model = Transaction
        fields = ['amount', 'date', 'category']

class BudgetForm(forms.ModelForm):
    """
    Form for setting or updating a budget
    """
    class Meta:# pylint: disable=too-few-public-methods
        """
        meta class
        """
        model = Budget
        fields = ['total_amount']
        labels = {'total_amount': 'Set Your Budget'}

class ContactForm(forms.Form):
    """
    Form for contact message
    """
    name = forms.CharField(
    max_length=100,
    widget=forms.TextInput(attrs={'placeholder': 'Your Name'})
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    subject = forms.CharField(
    max_length=200,
    widget=forms.TextInput(attrs={'placeholder': 'Subject'})
    )
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message'}))

class SavingsGoalForm(forms.ModelForm):
    """
    Form for creating or updating savings goals
    """
    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta class
        """
        model = SavingsGoal
        fields = ['name', 'target_amount', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class SavingsTransactionForm(forms.ModelForm):
    """
    Form for logging transactions toward a savings goal
    """
    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta class
        """
        model = SavingsTransaction
        fields = ['amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
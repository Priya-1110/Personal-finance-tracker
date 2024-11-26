"""This module contains the forms for the finance app."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from .models import Transaction, Budget, SavingsGoal, SavingsTransaction, UserImage

# Define regex validators
email_regex = RegexValidator(
    regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    message="Please enter a valid email address."
)
name_regex = RegexValidator(
    regex=r'^[a-zA-Z\s-]{2,30}$',
    message=(
        "Name should only contain letters, spaces, or hyphens, "
        "and be between 2 to 30 characters long."
    )
)


class UserRegisterForm(UserCreationForm): # pylint: disable=too-many-ancestors
    """
    Custom form for user registration
    """
    email = forms.EmailField(
        required=True,
        validators=[email_regex]
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        validators=[name_regex]
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        validators=[name_regex]
    )

    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta class for User registration fields
        """
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class IncomeForm(forms.ModelForm):
    """
    Form for adding income transactions
    """
    amount = forms.DecimalField(
        validators=[MinValueValidator(0.01, "Amount must be positive.")]
    )

    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta class for Income fields
        """
        model = Transaction
        fields = ['amount', 'date', 'category']

class BudgetForm(forms.ModelForm):
    """
    Form for setting or updating a budget
    """
    total_amount = forms.DecimalField(
        validators=[MinValueValidator(0.01, "Budget amount must be positive.")]
    )

    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta class for Budget fields
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
        widget=forms.TextInput(attrs={'placeholder': 'Your Name'}),
        validators=[name_regex]
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}),
        validators=[email_regex]
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Subject'}),
        validators=[
            RegexValidator(regex=r'^.{5,}$', message="Subject must be at least 5 characters long.")
        ]
    )
    message = forms.CharField(
    widget=forms.Textarea(attrs={'placeholder': 'Your Message'}),
    validators=[
        RegexValidator(
            regex=r'^.{10,}$',
            message="Message must be at least 10 characters long."
        )
    ]
)


class SavingsGoalForm(forms.ModelForm):
    """
    Form for creating or updating savings goals
    """
    target_amount = forms.DecimalField(
        validators=[MinValueValidator(0.01, "Target amount must be positive.")]
    )

    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta class for SavingsGoal fields
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
    amount = forms.DecimalField(
        validators=[MinValueValidator(0.01, "Transaction amount must be positive.")]
    )

    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta class for SavingsTransaction fields
        """
        model = SavingsTransaction
        fields = ['amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class UserImageForm(forms.ModelForm):
    """
    Form for uploading a user image
    """
    class Meta: # pylint: disable=too-few-public-methods
        """
        Meta class for userimage fields
        """
        model = UserImage
        fields = ['image']

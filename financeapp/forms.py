from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction, Budget, Contact, SavingsGoal, SavingsTransaction

# Custom form for user registration
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Adding email field
    first_name = forms.CharField(max_length=30, required=True)  # First name field
    last_name = forms.CharField(max_length=30, required=True)  # Last name field
    
    class Meta:
        model = User  # The form will create or update the User model instance
        fields = ['first_name', 'last_name','username', 'email', 'password1', 'password2']  # Specify the fields
        
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'category']  # Exclude 'type' as it's set in the view
        
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['total_amount'] 
        labels = {'total_amount': 'Set Your Budget'}
        
class ContactForm(forms.Form):
    """Form for contact messages"""
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message'}))
    
class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'deadline'] 
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class SavingsTransactionForm(forms.ModelForm):
    class Meta:
        model = SavingsTransaction
        fields = ['amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
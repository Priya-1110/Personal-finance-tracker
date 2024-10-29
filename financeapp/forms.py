from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Custom form for user registration
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Adding email field
    first_name = forms.CharField(max_length=30, required=True)  # First name field
    last_name = forms.CharField(max_length=30, required=True)  # Last name field
    
    class Meta:
        model = User  # The form will create or update the User model instance
        fields = ['first_name', 'last_name','username', 'email', 'password1', 'password2']  # Specify the fields
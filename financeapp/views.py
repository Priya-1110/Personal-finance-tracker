from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate  # Import for user authentication and login functions
from django.contrib.auth.forms import AuthenticationForm  # Django's built-in login form
from .forms import UserRegisterForm  # Import the registration form we just created
from django.contrib.auth.models import User
# Create your views here.
def home(request):
    return render(request, 'home.html')
    
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')

            # Check if the email is already registered and active
            if User.objects.filter(email=email, is_active=True).exists():
                form.add_error('email', 'This email is already registered.')
            else:
                # If email is new, create the user
                user = form.save()
                login(request, user)  # Automatically log the user in
                return redirect('login')  # Redirect after successful registration
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})

# View for user login
def login_view(request):
    if request.method == 'POST':  # If the form is submitted (POST request)
        form = AuthenticationForm(request, data=request.POST)  # Create an instance of Django's built-in login form
        if form.is_valid():  # Check if the login form is valid
            username = form.cleaned_data.get('username')  # Get the username from the form data
            password = form.cleaned_data.get('password')  # Get the password from the form data
            user = authenticate(username=username, password=password)  # Authenticate the user with provided credentials
            if user is not None:  # If authentication is successful
                login(request, user)  # Log the user in
                return redirect('home')  # Redirect to the homepage
    else:
        form = AuthenticationForm()  # If not a POST request, create an empty login form
    return render(request, 'registration/login.html', {'form': form})  # Render the login template with the form

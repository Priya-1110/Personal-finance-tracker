from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, IncomeForm, BudgetForm, ContactForm
from .models import Transaction, Budget,Contact
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
import pandas as pd
from django.db.models import Sum
import json
import io
import xlsxwriter
import matplotlib.pyplot as plt
import base64
import matplotlib
from django.core.mail import send_mail
from django.conf import settings
from .models import SavingsGoal, SavingsTransaction
from .forms import SavingsGoalForm, SavingsTransactionForm




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
                return redirect('dashboard')  # Redirect to the dashboard after successful registration
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})

# View for user login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to the dashboard after successful login
    else:
        form = AuthenticationForm()  # If not a POST request, create an empty login form
    return render(request, 'registration/login.html', {'form': form})  # Render the login template with the form
    
@login_required  # Ensure only authenticated users can access the dashboard
def dashboard(request):
    return render(request, 'dashboard.html')


    
@login_required
def view_budget(request):
    budget, created = Budget.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(user=request.user)

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('view_budget') # Redirect to avoid form resubmission
    else:
        form = BudgetForm(instance=budget)

    # Calculate income, expenses, and balance
    total_income = sum(t.amount for t in transactions if t.type == Transaction.INCOME)
    total_expenses = sum(t.amount for t in transactions if t.type == Transaction.EXPENSE)
    balance =  total_income - total_expenses
    budget_difference = budget.total_amount - total_expenses


    context = {
        'budget': budget, 
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'budget_difference': budget_difference,  
        'form': form,  # Add the form to the context
    }
    return render(request, 'view_budget.html', context) 

@login_required
def savings_goals_view(request):
    goals = SavingsGoal.objects.filter(user=request.user)

    # Calculate and add target_dollars and current_dollars to each goal
    for goal in goals:
        goal.target_dollars = goal.target_amount 
        goal.current_dollars = goal.current_amount 

    return render(request, 'savings_goals.html', {'goals': goals})


@login_required
def add_savings_goal(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)  
            goal.user = request.user  
            goal.save()
            return redirect('savings_goals')
    else:
        form = SavingsGoalForm()
    return render(request, 'add_savings_goal.html', {'form': form})

@login_required
def log_savings(request, goal_id):
    goal = get_object_or_404(SavingsGoal, pk=goal_id, user=request.user) 
    if request.method == 'POST':
        form = SavingsTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.goal = goal
            transaction.save()

            # Update goal's current amount
            goal.current_amount += transaction.amount
            goal.save() 

            return redirect('savings_goals')
    else:
        form = SavingsTransactionForm()
    return render(request, 'log_savings.html', {'form': form, 'goal': goal})


@login_required
def add_transaction(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category = request.POST.get('category')
        transaction_type = request.POST.get('type')
        
        # Ensure date input is in the correct format and timezone
        if date:
            date = timezone.datetime.strptime(date, "%Y-%m-%d").date()

        # Create and save the transaction
        transaction = Transaction(
            user=request.user,
            amount=amount,
            date=date,
            category=category,
            type=transaction_type
        )
        transaction.save()

        # Redirect to the transactions view or dashboard after saving
        return redirect('view_transactions')

    return render(request, 'add_transaction.html')

@login_required   
def view_transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    # Get filter parameters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category = request.GET.get('category')
    transaction_type = request.GET.get('type')

    
    if from_date:
        transactions = transactions.filter(date__gte=from_date)
    if to_date:
        transactions = transactions.filter(date__lte=to_date)
    if category:
        transactions = transactions.filter(category__icontains=category)
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)

    return render(request, 'view_transactions.html', {'transactions': transactions})

# View for editing a transaction
def edit_transaction(request, transaction_id):
    if request.method == 'POST':
        transaction = Transaction.objects.get(id=transaction_id)
        transaction.amount = request.POST['amount']
        transaction.date = request.POST['date']
        transaction.category = request.POST['category']
        transaction.type = request.POST['type']
        transaction.save()
        return redirect('view_transactions')  # Redirect to the view transactions page

# View for deleting a transaction
@require_POST
def delete_transaction(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    transaction.delete()
    return redirect('view_transactions')  # Redirect to the view transactions page
    
# def view_transactions(request):
#     # Get filter parameters from the GET request
#     from_date = request.GET.get('from_date')
#     to_date = request.GET.get('to_date')
#     category = request.GET.get('category', '').strip()  # Default to an empty string
#     transaction_type = request.GET.get('type', '')  # Default to all types

#     # Start with all transactions
#     transactions = Transaction.objects.all()

#     # Filter by date range if specified
#     if from_date and to_date:
#         transactions = transactions.filter(date__range=[from_date, to_date])

#     # Filter by category if specified
#     if category:
#         transactions = transactions.filter(category__icontains=category)

#     # Filter by transaction type if specified
#     if transaction_type:
#         transactions = transactions.filter(type=transaction_type)

#     # Render the view with the filtered transactions
#     return render(request, 'view_transactions.html', {'transactions': transactions})

# @login_required
# def view_transactions(request):
#     transactions = Transaction.objects.filter(user=request.user)  # Get transactions for the logged-in user
#     return render(request, 'view_transactions.html', {'transactions': transactions})

@login_required
def logout(request):
    auth_logout(request)  # Log the user out
    return redirect('home')  # Redirect to home page after logout
    

# @login_required
# def reports(request):
#     # Initialize variables
#     transactions = Transaction.objects.filter(user=request.user)
#     chart = None
#     from_date = request.POST.get('from_date', '')
#     to_date = request.POST.get('to_date', '')
#     category = request.POST.get('category', '')
#     transaction_type = request.POST.get('type', '')

#     # Filter transactions based on user input
#     if request.method == 'POST':
#         if from_date:
#             transactions = transactions.filter(date__gte=from_date)
#         if to_date:
#             transactions = transactions.filter(date__lte=to_date)
#         if transaction_type:
#             transactions = transactions.filter(type=transaction_type)

#         # Generate chart based on filtered transactions
#         if transactions.exists():
#             # Prepare data for the chart
#             categories = transactions.values('category').annotate(total=Sum('amount'))
#             labels = [cat['category'] for cat in categories]
#             totals = [cat['total'] for cat in categories]

#             # Create a pie chart
#             plt.figure(figsize=(8, 6))
#             plt.pie(totals, labels=labels, autopct='%1.1f%%')
#             plt.title('Transaction Distribution by Category')

#             # Save the plot to a BytesIO object
#             buf = io.BytesIO()
#             plt.savefig(buf, format='png')
#             plt.close()
#             buf.seek(0)
#             chart = base64.b64encode(buf.read()).decode('utf-8')

#     return render(request, 'reports.html', {'chart': chart})
  


@login_required
def reports(request):
    # Initialize variables
    transactions = Transaction.objects.filter(user=request.user)
    chart_data = None
    from_date = request.POST.get('from_date', '')
    to_date = request.POST.get('to_date', '')
    transaction_type = request.POST.get('type', '')

    # Filter transactions based on user input
    if request.method == 'POST':
        if from_date:
            transactions = transactions.filter(date__gte=from_date)
        if to_date:
            transactions = transactions.filter(date__lte=to_date)
        if transaction_type:
            transactions = transactions.filter(type=transaction_type)

        # Generate data for charts
        if transactions.exists():
            categories = transactions.values('category').annotate(total=Sum('amount'))
            labels = [cat['category'] for cat in categories]
            totals = [float(cat['total']) for cat in categories]  # Convert Decimal to float
            
            # Prepare data for JSON
            chart_data = json.dumps({
                'labels': labels,
                'totals': totals
            })

    return render(request, 'reports.html', {'chart_data': chart_data})


def download_transactions_csv(request):
    # Get the filtering parameters from the request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category = request.GET.get('category')
    transaction_type = request.GET.get('type')

    # Get the user's transactions and apply filters
    transactions = Transaction.objects.filter(user=request.user)

    if from_date:
        transactions = transactions.filter(date__gte=from_date)
    if to_date:
        transactions = transactions.filter(date__lte=to_date)
    if category:
        transactions = transactions.filter(category__icontains=category)
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)

    # Create a DataFrame from the filtered transactions
    df = pd.DataFrame(list(transactions.values('date', 'category', 'amount', 'type')))

    # Create the HTTP response with the appropriate content type for CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    # Write the DataFrame to the response
    df.to_csv(path_or_buf=response, index=False)

    return response

def download_transactions_excel(request):
    # Get the filtering parameters from the request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category = request.GET.get('category')
    transaction_type = request.GET.get('type')

    # Get the user's transactions and apply filters
    transactions = Transaction.objects.filter(user=request.user)

    if from_date:
        transactions = transactions.filter(date__gte=from_date)
    if to_date:
        transactions = transactions.filter(date__lte=to_date)
    if category:
        transactions = transactions.filter(category__icontains=category)
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)

    # Create a DataFrame from the filtered transactions
    df = pd.DataFrame(list(transactions.values('date', 'category', 'amount', 'type')))

    # Create the HTTP response with the appropriate content type for Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'

    # Write the DataFrame to an Excel file
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')

    return response
def contact_view(request):
    """Contact form view to send messages"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send the email
            send_mail(
                f'Message from {name} <{email}>',
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['priyashan112002@gmail.com'],
                fail_silently=False, 
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')  # Redirect to the contact view itself
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
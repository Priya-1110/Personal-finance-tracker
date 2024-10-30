from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, IncomeForm
from .models import Transaction
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import pandas as pd
from django.db.models import Sum
import json
import io
from django.http import HttpResponse
import xlsxwriter
import matplotlib.pyplot as plt
import base64
import matplotlib


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

    
def view_transactions(request):
    # Logic to retrieve and display transactions
    return render(request, 'view_transactions.html')

# @login_required
# def add_income(request):
#     if request.method == 'POST':
#         form = IncomeForm(request.POST)
#         if form.is_valid():
#             income = form.save(commit=False)  # Get form data without saving yet
#             income.user = request.user         # Associate income with the logged-in user
#             income.date = timezone.now()       # Set the date to the current time if not in form
#             income.type = 'Income'             # Ensure the type is set to "Income"
#             income.save()                      # Save to the database
#             messages.success(request, 'Income added successfully!')
#             return redirect('dashboard')       # Redirect to dashboard or income view
#         else:
#             messages.error(request, 'Please correct the errors below.')
#     else:
#         form = IncomeForm()

#     return render(request, 'add_income.html', {'form': form})

# def add_expense(request):
#     # Logic to add expense
#     return render(request, 'add_expense.html')

def view_budget(request):
    # Logic to view budget
    return render(request, 'view_budget.html')

def savings_goals(request):
    # Logic to manage savings goals
    return render(request, 'savings_goals.html')

def reports(request):
    # Logic to generate reports
    return render(request, 'reports.html')

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


# View for viewing transactions
def view_transactions(request):
    # Get filter parameters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category = request.GET.get('category')
    transaction_type = request.GET.get('type')

    # Querying the database based on filters
    transactions = Transaction.objects.all()
    
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
    

# Ensure 'Agg' backend is used for non-GUI environments
matplotlib.use('Agg')

def export_excel(transactions):
    # Use a buffer to store the Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame(list(transactions.values('date', 'category', 'type', 'amount')))
        df.to_excel(writer, index=False, sheet_name='Transactions')
    
    output.seek(0)
    return output

def generate_report(request):
    # Extract filters from GET parameters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category = request.GET.get('category')
    transaction_type = request.GET.get('type')

    # Query transactions with filters
    transactions = Transaction.objects.all()
    if from_date and to_date:
        transactions = transactions.filter(date__range=[from_date, to_date])
    if category:
        transactions = transactions.filter(category=category)
    if transaction_type:
        transactions = transactions.filter(type=transaction_type)

    # Aggregate data for charts
    income_sum = transactions.filter(type="Income").aggregate(Sum('amount'))['amount__sum'] or 0
    expense_sum = transactions.filter(type="Expense").aggregate(Sum('amount'))['amount__sum'] or 0
    net_savings = income_sum - expense_sum

    # Category-wise breakdown for the chart
    category_breakdown = (
        transactions
        .values('category')
        .annotate(total_amount=Sum('amount'))
        .order_by('-total_amount')
    )

    # Convert to DataFrame for Matplotlib
    category_df = pd.DataFrame(list(category_breakdown))

    # Generate bar chart using Matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(category_df['category'], category_df['total_amount'], color='skyblue')
    plt.xlabel('Category')
    plt.ylabel('Total Amount')
    plt.title('Category Breakdown')

    # Save chart to a PNG image in memory
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png')
    chart_buffer.seek(0)
    chart_base64 = base64.b64encode(chart_buffer.getvalue()).decode('utf-8')
    plt.close()

    # Export CSV if requested
    if request.GET.get('export') == 'csv':
        df = pd.DataFrame(list(transactions.values('date', 'category', 'type', 'amount')))
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=report.csv'
        df.to_csv(path_or_buf=response, index=False)
        return response

    # Export Excel if requested
    if request.GET.get('export') == 'excel':
        output = export_excel(transactions)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=report.xlsx'
        return response

    # Context data for the HTML template
    context = {
        'transactions': transactions,
        'income_sum': income_sum,
        'expense_sum': expense_sum,
        'net_savings': net_savings,
        'category_chart': chart_base64,  # Pass encoded image to template
    }

    return render(request, 'reports.html', context)

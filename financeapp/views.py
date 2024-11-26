"""
This module contains the views for the finance app.
"""
import json
import logging
import pandas as pd
import requests
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegisterForm, BudgetForm, ContactForm
from .forms import SavingsGoalForm, SavingsTransactionForm, UserImageForm
from .models import Transaction, Budget, Notification, SavingsGoal, UserImage

logger = logging.getLogger(__name__)


def home(request):
    """
    Displays homepage with an option to login or register.
    """
    return render(request, 'home.html')


def register(request):
    """
    Allows the user to register with their email ID.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email, is_active=True).exists():
                form.add_error('email', 'This email is already registered.')
            else:
                user = form.save()
                login(request, user)
                messages.success(request, f'Account created for {email}. You are now logged in.')
                return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """
    Allows the registered user to log in.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def dashboard(request):
    """
    Displays the main page after logging in.
    """
    return render(request, 'dashboard.html')


@login_required
def view_budget(request):
    """
    Allows the user to input their budget and keep track of expenses.
    """
    budget, _ = Budget.objects.get_or_create(user=request.user) # pylint: disable=no-member
    transactions = Transaction.objects.filter(user=request.user) # pylint: disable=no-member

    total_income = sum(t.amount for t in transactions if t.type == Transaction.INCOME)
    total_expenses = sum(t.amount for t in transactions if t.type == Transaction.EXPENSE)
    balance = total_income - total_expenses
    budget_difference = budget.total_amount - total_expenses

    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            with transaction.atomic():
                form.save()
                if form.has_changed():
                    Notification.objects.filter(  # pylint: disable=no-member
                        user=request.user,
                        link=reverse('view_budget')
                    ).delete()  # pylint: disable=no-member
                    create_notification(
                        request.user,
                        message=(
                            f"You have exceeded your total budget for this month! "
                            f"You are ${abs(budget_difference):.2f} over budget."
                        ),
                        link=reverse('view_budget')
                    )
                return redirect('view_budget')
        else:
            form = BudgetForm(instance=budget)
        if total_expenses > budget.total_amount:
            Notification.objects.filter(  # pylint: disable=no-member
                user=request.user,
                link=reverse('view_budget')
            ).delete()  # pylint: disable=no-member
            create_notification(
                request.user,
                message=(
                    f"You have exceeded your total budget for this month! "
                    f"You are ${abs(budget_difference):.2f} over budget."
                ),
                link=reverse('view_budget')
            )
        context = {
        'budget': budget,
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'budget_difference': budget_difference,
        'form': form,
    }
    return render(request, 'view_budget.html', context)


@login_required
def savings_goals_view(request):
    """
    Displays a list of the user's savings goals.
    """
    goals = SavingsGoal.objects.filter(user=request.user) # pylint: disable=no-member
    for goal in goals:
        goal.target_dollars = goal.target_amount
        goal.current_dollars = goal.current_amount

    return render(request, 'savings_goals.html', {'goals': goals})


@login_required
def add_savings_goal(request):
    """
    Takes input from the user about their savings goals and adds it to the database.
    """
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
    """
    Allows the user to log their savings for a particular goal.
    """
    goal = get_object_or_404(SavingsGoal, pk=goal_id, user=request.user)
    if request.method == 'POST':
        form = SavingsTransactionForm(request.POST)
        if form.is_valid():
            new_transaction = form.save(commit=False)
            new_transaction.goal = goal
            new_transaction.save()
            goal.current_amount += new_transaction.amount
            goal.save()

            if goal.current_amount >= goal.target_amount:
                message = f"Congratulations! You've reached your savings goal of ${goal.target_amount:.2f}."
                create_notification(request.user, message, link=f"/goals/{goal.id}/")

            return redirect('savings_goals')
    else:
        form = SavingsTransactionForm()

    return render(request, 'log_savings.html', {'form': form, 'goal': goal})


@login_required
def add_transaction(request):
    """
    Allows the user to add all kinds of transactions.
    """
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category = request.POST.get('category')
        transaction_type = request.POST.get('type')

        if date:
            date = timezone.datetime.strptime(date, "%Y-%m-%d").date()

        new_transaction = Transaction(
            user=request.user,
            amount=amount,
            date=date,
            category=category,
            type=transaction_type
        )
        new_transaction.save()
        return redirect('dashboard')

    return render(request, 'add_transaction.html')


@login_required
def view_transactions(request):
    """
    Enables the user to view their transactions with an added functionality of filters.
    """
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')  # pylint: disable=no-member
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


@login_required
def edit_transaction(request, transaction_id):
    """
    Permits the user to edit the transactions.
    """
    if request.method == 'POST':
        editable_transaction = Transaction.objects.get(id=transaction_id)  # pylint: disable=no-member
        editable_transaction.amount = request.POST['amount']
        editable_transaction.date = request.POST['date']
        editable_transaction.category = request.POST['category']
        editable_transaction.type = request.POST['type']
        editable_transaction.save()
        return redirect('view_transactions')

    return HttpResponse("Invalid request method")  # Handle non-POST requests.


@require_POST
def delete_transaction(request, transaction_id):
    """
    Permits the user to delete the transaction.
    """
    deletable_transaction = get_object_or_404(Transaction, id=transaction_id)  # Fetch transaction or return 404
    # Log deletion for audit purposes using lazy % formatting
    logger.info("User %s deleted transaction ID %d", request.user, transaction_id)
    deletable_transaction.delete()
    return redirect('view_transactions')  # Redirect to the view transactions page.



@login_required
def logout(request):
    """
    Log the user out
    """
    auth_logout(request)
    return redirect('home')  # Redirect to home page after logout

@login_required
def reports(request):
    """
    Generates financial insights about the users spendings and earnings
    """
    transactions = Transaction.objects.filter(user=request.user) # pylint: disable=no-member
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
            chart_data = json.dumps({ # pylint: disable=no-member
                'labels': labels,
                'totals': totals
            })

    return render(request, 'reports.html', {'chart_data': chart_data})


def download_transactions_csv(request):
    """
    Allows the user to download their transactions in CSV format
    """
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category = request.GET.get('category')
    transaction_type = request.GET.get('type')

    # Get the user's transactions and apply filters
    transactions = Transaction.objects.filter(user=request.user) # pylint: disable=no-member

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
    """
    Allows the user to download their transactions in Excel format
    """
    # Get the filtering parameters from the request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category = request.GET.get('category')
    transaction_type = request.GET.get('type')

    # Get the user's transactions and apply filters
    transactions = Transaction.objects.filter(user=request.user) # pylint: disable=no-member

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
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'

    # Write the DataFrame to an Excel file
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transactions')

    return response
def contact_view(request):
    """
    Handles the contact form submission to send messages.
    """
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
        # Clear the form and prepare for a new submission
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def create_notification(user, message, link=None):
    """
    Creates an in-app notification for the specified user.
    
    Args:
        user: The user to whom the notification will be sent.
        message: The notification message.
        link: Optional link related to the notification.
    """
    Notification.objects.create(user=user, message=message, link=link)  # pylint: disable=no-member


@login_required
def alerts(request):
    """
    Displays unread notifications for the logged-in user.
    """
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)  # pylint: disable=no-member
    context = {'unread_notifications': unread_notifications}
    return render(request, 'alerts.html', context)


@login_required
def mark_notification_as_read(request, notification_id):
    """
    Marks a specific notification as read for the logged-in user.
    
    Args:
        notification_id: The ID of the notification to be marked as read.
    """
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('alerts')  # Redirect back to the alerts page


def upload_image(request):
    """
    Handles the uploading of bills and receipts by the user.
    """
    if request.method == 'POST':
        form = UserImageForm(request.POST, request.FILES)
        if form.is_valid():
            user_image = form.save(commit=False)
            user_image.user = request.user
            user_image.save()
            messages.success(request, 'Receipt has been uploaded successfully!')
            form = UserImageForm()  # Reset the form after successful upload
    else:
        form = UserImageForm()
    return render(request, 'upload_image.html', {'form': form})


API_URL = "https://api.exchangerate.host/convert"
API_KEY = "68d3237580165ad3c12880c9f14e4ec0"  # Avoid hardcoding in production


def fetch_data_with_timeout(url):
    """
    Fetches data from a URL with a timeout to prevent indefinite hangs.

    Args:
        url: The URL to fetch data from.

    Returns:
        Response data if successful, None otherwise.
    """
    try:
        response = requests.get(url, timeout=5)  # 5-second timeout
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


@login_required
def image_gallery(request):
    """
    Displays all images uploaded by the logged-in user.
    """
    user_images = UserImage.objects.filter(user=request.user) # pylint: disable=no-member
    return render(request, 'image_gallery.html', {'user_images': user_images})


@login_required
def delete_image(request, image_id):
    """
    Allows the logged-in user to delete a specific uploaded image.

    Args:
        image_id: ID of the image to be deleted.
    """
    image = get_object_or_404(UserImage, id=image_id, user=request.user)
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully.')
        return redirect('image_gallery')

    messages.error(request, 'Invalid request.')
    return redirect('dashboard')


def currency_converter(request):
    """
    Converts currency based on user input using the Exchange Rate API.
    """
    if request.method == "POST":
        base = request.POST.get("base")  # Base currency
        target = request.POST.get("target")  # Target currency
        amount = float(request.POST.get("amount", 0))  # Amount to convert

        # API request
        response = requests.get(
            API_URL,
            params={
                "access_key": API_KEY,
                "from": base,
                "to": target,
                "amount": amount,
            },
            timeout=5,  # Added timeout
        )

        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                converted_amount = data['result']
                context = {
                    "converted_amount": converted_amount,
                    "base": base,
                    "target": target,
                    "amount": amount,
                }
                return render(request, "currency_converter/result.html", context)
            return render(request, "currency_converter/index.html", {"error": "Conversion failed, invalid response."})

        return render(request, "currency_converter/index.html", {"error": "Failed to fetch currency rates."})

    return render(request, "currency_converter/index.html")
    
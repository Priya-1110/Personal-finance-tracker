from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Budget, Transaction
from django.conf import settings
from django.db.models import Sum

def check_budgets():
    users = User.objects.all()

    for user in users:
        try:
            budget = Budget.objects.get(user=user)
            amount_spent = Transaction.objects.filter(user=user).aggregate(total_spent=Sum('amount'))['total_spent'] or 0

            if amount_spent > budget.total_amount and not budget.alert_sent:
                send_mail(
                    subject="Budget Exceeded Alert!",
                    message=f"Dear {user.username},\n\nYou have exceeded your budget limit of {budget.total_amount}. You have currently spent {amount_spent}.\nPlease review your expenses to stay on track.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                print(f"Alert email sent to {user.username} for exceeding budget.")

                # Set alert_sent to True to prevent further alerts
                budget.alert_sent = True 
                budget.save()

        except Budget.DoesNotExist:
            print(f"No budget set for user {user.username}")
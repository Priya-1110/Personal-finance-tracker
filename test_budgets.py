import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adminproject.settings') 
django.setup()

from financeapp.tasks import check_budgets 

if __name__ == "__main__":
    check_budgets()
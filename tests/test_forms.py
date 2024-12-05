import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from financeapp.forms import (
    UserRegisterForm,
    UserImageForm,
    IncomeForm,
    BudgetForm,
    ContactForm,
    SavingsGoalForm,
    SavingsTransactionForm,
)
from financeapp.models import Transaction, Budget, SavingsGoal, SavingsTransaction


@pytest.mark.django_db
def test_user_register_form_valid_data():
    form = UserRegisterForm(data={
        'first_name': 'Priya',
        'last_name': 'Shanmugam',
        'username': 'priya123',
        'email': 'priya@example.com',
        'password1': 'StrongPassword123!',
        'password2': 'StrongPassword123!',
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_user_register_form_invalid_email():
    form = UserRegisterForm(data={
        'first_name': 'Priya',
        'last_name': 'Shanmugam',
        'username': 'priya123',
        'email': 'invalid-email',
        'password1': 'StrongPassword123!',
        'password2': 'StrongPassword123!',
    })
    assert not form.is_valid()
    assert 'email' in form.errors


@pytest.mark.django_db
def test_income_form_valid_data():
    form = IncomeForm(data={
        'amount': 1000.50,
        'date': '2024-12-04',
        'category': 'Salary',
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_budget_form_valid_data():
    form = BudgetForm(data={
        'total_amount': 5000,
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_contact_form_valid_data():
    form = ContactForm(data={
        'name': 'Priya Shanmugam',
        'email': 'priya@example.com',
        'subject': 'Inquiry about savings',
        'message': 'Can I have more details about the savings goals?',
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_contact_form_invalid_message():
    form = ContactForm(data={
        'name': 'Priya Shanmugam',
        'email': 'priya@example.com',
        'subject': 'Help',
        'message': 'Short',
    })
    assert not form.is_valid()
    assert 'message' in form.errors


@pytest.mark.django_db
def test_savings_goal_form_valid_data():
    form = SavingsGoalForm(data={
        'name': 'Vacation Fund',
        'target_amount': 2000,
        'deadline': '2025-01-01',
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_savings_transaction_form_valid_data():
    form = SavingsTransactionForm(data={
        'amount': 500,
        'date': '2024-12-04',
    })
    assert form.is_valid()




import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from financeapp.models import Budget, Transaction


@pytest.fixture
def user():
    """
    Fixture to create a test user.
    """
    return User.objects.create_user(username='testuser', password='testpassword')


@pytest.fixture
def client():
    """
    Fixture to provide the Django test client.
    """
    return Client()


@pytest.fixture
def create_budget(user):
    """
    Fixture to create a budget associated with a user.
    """
    return Budget.objects.create(user=user, total_amount=1000)


@pytest.fixture
def create_transaction(user):
    """
    Fixture to create a transaction associated with a user.
    """
    return Transaction.objects.create(
        user=user, amount=100, type=Transaction.EXPENSE, category="Food"
    )


@pytest.mark.django_db
def test_homepage(client):
    """
    Test that the homepage loads successfully and contains the expected content.
    """
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert 'Login' in response.content.decode()


@pytest.mark.django_db
def test_register_user(client):
    """
    Test user registration functionality.
    """
    data = {
        'email': 'testuser@example.com',
        'password1': 'password123',
        'password2': 'password123',
    }
    response = client.post(reverse('register'), data)
    assert response.status_code == 302  # Redirect to dashboard after registration
    assert User.objects.filter(email='testuser@example.com').exists()


@pytest.mark.django_db
def test_login_user(client, user):
    """
    Test user login functionality.
    """
    response = client.post(
        reverse('login_view'), {'username': user.username, 'password': 'testpassword'}
    )
    assert response.status_code == 302  # Redirect to dashboard after login
    assert 'dashboard' in response.url


@pytest.mark.django_db
def test_dashboard_view(client, user):
    """
    Test access to the dashboard after logging in.
    """
    client.login(username=user.username, password='testpassword')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert 'Dashboard' in response.content.decode()


@pytest.mark.django_db
def test_add_budget(client, user):
    """
    Test budget creation and its workflow.
    """
    client.login(username=user.username, password='testpassword')
    response = client.get(reverse('view_budget'))
    assert response.status_code == 200
    assert 'Budget' in response.content.decode()

    data = {'total_amount': 1500}
    response = client.post(reverse('view_budget'), data)
    assert response.status_code == 302  # Redirect after saving the budget
    budget = Budget.objects.get(user=user)
    assert budget.total_amount == 1500


@pytest.mark.django_db
def test_add_transaction(client, user, create_budget):
    """
    Test adding a transaction.
    """
    client.login(username=user.username, password='testpassword')
    response = client.get(reverse('add_transaction'))
    assert response.status_code == 200
    assert 'Add Transaction' in response.content.decode()

    data = {
        'amount': 200,
        'date': '2024-12-01',
        'category': 'Groceries',
        'type': 'EXPENSE',
    }
    response = client.post(reverse('add_transaction'), data)
    assert response.status_code == 302  # Redirect after saving the transaction
    transaction = Transaction.objects.get(user=user)
    assert transaction.amount == 200


@pytest.mark.django_db
def test_view_transactions(client, user, create_transaction):
    """
    Test the view transactions page.
    """
    client.login(username=user.username, password='testpassword')
    response = client.get(reverse('view_transactions'))
    assert response.status_code == 200
    assert 'Transactions' in response.content.decode()


@pytest.mark.django_db
def test_logout(client, user):
    """
    Test user logout functionality.
    """
    client.login(username=user.username, password='testpassword')
    response = client.get(reverse('logout'))
    assert response.status_code == 302  # Redirect to home after logout
    assert 'home' in response.url


@pytest.mark.django_db
def test_reports_view(client, user, create_transaction):
    """
    Test viewing generated reports.
    """
    client.login(username=user.username, password='testpassword')
    response = client.get(reverse('reports'))
    assert response.status_code == 200
    assert 'Reports' in response.content.decode()


@pytest.mark.django_db
def test_download_transactions_csv(client, user, create_transaction):
    """
    Test downloading transactions in CSV format.
    """
    client.login(username=user.username, password='testpassword')
    response = client.get(reverse('download_transactions_csv'))
    assert response.status_code == 200
    assert response['Content-Type'] == 'text/csv'


@pytest.mark.django_db
def test_download_transactions_excel(client, user, create_transaction):
    """
    Test downloading transactions in Excel format.
    """
    client.login(username=user.username, password='testpassword')
    response = client.get(reverse('download_transactions_excel'))
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

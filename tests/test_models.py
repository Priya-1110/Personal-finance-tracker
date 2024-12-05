import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from financeapp.models import Transaction, Budget, Contact, SavingsGoal, SavingsTransaction, Notification, UserImage
from decimal import Decimal
from django.db import IntegrityError

@pytest.mark.django_db
def test_transaction_creation():
    # Create a user instance
    user = User.objects.create_user(username="testuser", password="testpassword")

    # Create a transaction
    transaction = Transaction.objects.create(
        user=user,
        amount=Decimal('100.00'),
        date='2024-12-04',
        category="Food",
        type=Transaction.INCOME
    )

    # Test that the transaction is created correctly
    assert transaction.user.username == 'testuser'
    assert transaction.amount == Decimal('100.00')
    assert transaction.category == 'Food'
    assert transaction.type == 'Income'
    assert str(transaction) == "testuser - Food - Income - 100.00"

@pytest.mark.django_db
def test_budget_creation():
    user = User.objects.create_user(username="testuser", password="testpassword")
    budget = Budget.objects.create(user=user, total_amount=Decimal('500.00'))

    assert budget.user.username == 'testuser'
    assert budget.total_amount == Decimal('500.00')
    assert str(budget) == "testuser's Budget: $500.00"

@pytest.mark.django_db
def test_contact_creation():
    contact = Contact.objects.create(
        name="John Doe",
        email="john.doe@example.com",
        subject="Inquiry",
        message="I would like to know more about your services."
    )

    assert contact.name == "John Doe"
    assert contact.email == "john.doe@example.com"
    assert contact.subject == "Inquiry"
    assert len(contact.message) > 0
    assert str(contact) == "John Doe - Inquiry"

@pytest.mark.django_db
def test_savings_goal_creation():
    user = User.objects.create_user(username="testuser", password="testpassword")
    savings_goal = SavingsGoal.objects.create(
        user=user,
        name="Vacation Fund",
        target_amount=Decimal('2000.00'),
        current_amount=Decimal('500.00')
    )

    assert savings_goal.name == "Vacation Fund"
    assert savings_goal.target_amount == Decimal('2000.00')
    assert savings_goal.current_amount == Decimal('500.00')
    assert str(savings_goal) == "Vacation Fund - Target: $2000.00"

@pytest.mark.django_db
def test_savings_transaction_creation():
    user = User.objects.create_user(username="testuser", password="testpassword")
    savings_goal = SavingsGoal.objects.create(
        user=user,
        name="Vacation Fund",
        target_amount=Decimal('2000.00'),
        current_amount=Decimal('500.00')
    )
    savings_transaction = SavingsTransaction.objects.create(
        goal=savings_goal,
        amount=Decimal('100.00'),
        date='2024-12-04'
    )

    assert savings_transaction.amount == Decimal('100.00')
    assert savings_transaction.goal.name == "Vacation Fund"
    assert str(savings_transaction) == "$100.00 towards Vacation Fund on 2024-12-04"

@pytest.mark.django_db
def test_notification_creation():
    user = User.objects.create_user(username="testuser", password="testpassword")
    notification = Notification.objects.create(
        user=user,
        message="Your budget has been updated.",
        is_read=False
    )

    assert notification.user.username == 'testuser'
    assert notification.message == "Your budget has been updated."
    assert notification.is_read is False
    assert str(notification) == "Notification for testuser: Your budget has been updated."

@pytest.mark.django_db
def test_user_image_invalid_image():
    user = User.objects.create_user(username="testuser", password="testpassword")

    # Simulating an invalid image (e.g., a corrupted or non-image file)
    invalid_image = SimpleUploadedFile(
        name='test_file.txt',
        content=b'This is a text file, not an image.',
        content_type='text/plain'
    )

    with pytest.raises(IntegrityError):
        UserImage.objects.create(user=user, image=invalid_image)

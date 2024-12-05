# pylint: skip-file
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework import status
from financeapp.models import Transaction, Budget, SavingsGoal, UserImage, Notification

User = get_user_model()

@pytest.mark.django_db
class TestFinanceAppViews:

    @pytest.fixture
    def user(self):
        """
        Fixture to create a user.
        """
        return User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')

    @pytest.fixture
    def client(self, user):
        """
        Fixture to create a client and log in the user.
        """
        client = Client()
        client.login(username='testuser', password='testpassword')  # Log in the user
        return client

    def test_home_view(self, client):
        """
        Test the home view is rendered correctly.
        """
        response = client.get(reverse('home'))
        assert response.status_code == status.HTTP_200_OK
        assert 'home.html' in [template.name for template in response.templates]

    def test_view_budget(self, client, user):
        """
        Test viewing the user's budget.
        """
        Budget.objects.create(user=user, total_amount=1000)  # Associate the budget with the user
        response = client.get(reverse('view_budget'))
        assert response.status_code == status.HTTP_200_OK
        assert 'view_budget.html' in [template.name for template in response.templates]

    def test_view_transactions(self, client, user):
        """
        Test viewing the user's transactions.
        """
        Transaction.objects.create(user=user, amount=100, date='2023-10-01', category='Food', type='EXPENSE')
        response = client.get(reverse('view_transactions'))
        assert response.status_code == status.HTTP_200_OK
        assert 'view_transactions.html' in [template.name for template in response.templates]


    def test_alerts_view(self, client, user):
        """
        Test viewing the alerts or notifications page.
        """
        Notification.objects.create(user=user, message='Test alert')
        response = client.get(reverse('alerts'))
        assert response.status_code == status.HTTP_200_OK
        assert 'alerts.html' in [template.name for template in response.templates]

    def test_image_gallery_view(self, client, user):
        """
        Test viewing the user's image gallery.
        """
        UserImage.objects.create(user=user, image='test_image.jpg')  # Make sure to set the image properly
        response = client.get(reverse('image_gallery'))
        assert response.status_code == status.HTTP_200_OK
        assert 'image_gallery.html' in [template.name for template in response.templates]


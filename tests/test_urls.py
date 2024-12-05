import pytest
from django.urls import reverse, resolve
from financeapp import views


@pytest.mark.parametrize("url_name, view_func, kwargs", [
    ('home', views.home, None),
    ('login', views.login_view, None),
    ('register', views.register, None),
    ('dashboard', views.dashboard, None),
    ('view_transactions', views.view_transactions, None),
    ('edit_transaction', views.edit_transaction, {'transaction_id': 1}),
    ('delete_transaction', views.delete_transaction, {'transaction_id': 1}),
    ('view_budget', views.view_budget, None),
    ('savings_goals', views.savings_goals_view, None),
    ('add_savings_goal', views.add_savings_goal, None),
    ('log_savings', views.log_savings, {'goal_id': 1}),
    ('reports', views.reports, None),
    ('add_transaction', views.add_transaction, None),
    ('download_transactions_csv', views.download_transactions_csv, None),
    ('download_transactions_excel', views.download_transactions_excel, None),
    ('alerts', views.alerts, None),
    ('contact', views.contact_view, None),
    ('logout', views.logout, None),
    ('mark_notification_as_read', views.mark_notification_as_read, {'notification_id': 1}),
    ('upload_image', views.upload_image, None),
    ('image_gallery', views.image_gallery, None),
    ('delete_image', views.delete_image, {'image_id': 1}),
    ('currency_converter', views.currency_converter, None),
])
def test_url_patterns(url_name, view_func, kwargs):
    """
    Test that URL patterns resolve to the correct view functions.
    """
    url = reverse(url_name, kwargs=kwargs)
    assert resolve(url).func == view_func

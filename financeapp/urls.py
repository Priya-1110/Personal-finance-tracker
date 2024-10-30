from django.urls import path
from django.contrib.auth import views as auth_views  # Import Django's built-in authentication views
from . import views  # Import our custom views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('login/', views.login_view, name='login'),  # URL pattern for the login view
    path('register/', views.register, name='register'), # URL pattern for the register view
    path('dashboard/', views.dashboard, name='dashboard'), # URL pattern for the register view
    path('transactions/', views.view_transactions, name='view_transactions'),
    path('transactions/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    # path('view_transactions/', views.view_transactions, name='view_transactions'),
    # path('add_income/', views.add_income, name='add_income'),
    # path('add_expense/', views.add_expense, name='add_expense'),
    path('view_budget/', views.view_budget, name='view_budget'),
    path('savings_goals/', views.savings_goals, name='savings_goals'),
    path('reports/', views.reports, name='reports'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('logout/', views.logout, name='logout'),
]
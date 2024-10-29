from django.urls import path
from django.contrib.auth import views as auth_views  # Import Django's built-in authentication views
from . import views  # Import our custom views

urlpatterns = [
    path('', views.home, name='home'),  # Homepage
    path('login/', views.login_view, name='login'),  # URL pattern for the login view
    path('register/', views.register, name='register') # URL pattern for the register view
]
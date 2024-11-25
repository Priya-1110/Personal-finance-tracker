"""This module contains the URL patterns for the finance app."""

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transactions/', views.view_transactions, name='view_transactions'),
    path('transactions/edit/<int:transaction_id>/',
         views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:transaction_id>/',
         views.delete_transaction, name='delete_transaction'),
    
    path('view_budget/', views.view_budget, name='view_budget'),
    path('savings-goals/', views.savings_goals_view, name='savings_goals'),
    path('savings-goals/add/', views.add_savings_goal, name='add_savings_goal'),
    path('savings-goals/<int:goal_id>/log-savings/',
         views.log_savings, name='log_savings'),
    path('reports/', views.reports, name='reports'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('download/csv/', views.download_transactions_csv, name='download_transactions_csv'),
    path('download/excel/', views.download_transactions_excel,
         name='download_transactions_excel'),
    path('alerts/', views.alerts, name='alerts'),
    path('contact/', views.contact_view, name='contact'),
    path('logout/', views.logout, name='logout'),
    path(
        'alerts/mark-as-read/<int:notification_id>/',
        views.mark_notification_as_read,
        name='mark_notification_as_read'),
    # path('camera/', views.camera_view, name='camera'),
    # path('upload/', views.upload_image, name='upload_image'),
    path('upload/', views.upload_image, name='upload_image'),
    path('gallery/', views.image_gallery, name='image_gallery'),
    path('delete-image/<int:image_id>/', views.delete_image, name='delete_image'),
    path('currency/', views.currency_converter, name='currency_converter'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views

urlpatterns = [
    path('', views.donation_list, name='donate'),
    path('checkout/<int:donation_id>/', views.checkout, name='donation_checkout'),
    path('checkout/success/', views.checkout_success, name='donation_checkout_success'),
    path('pesapal/callback/', views.pesapal_callback, name='pesapal_callback'),
    path('contact/', views.contact_view, name='contact'),
    path('cause/<int:cause_id>/', views.donate_cause, name='donate_cause'),

    # Custom admin dashboard
    path('manage/', views.manage_donations, name='manage_donations'),
    path('manage/messages/', views.manage_messages, name='manage_messages'),
    path('manage/messages/<int:pk>/read/', views.mark_message_read, name='mark_message_read'),

    path('<int:pk>/', views.donation_detail, name='donation_detail'),
]
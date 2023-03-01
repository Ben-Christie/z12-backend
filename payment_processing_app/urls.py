from django.urls import path
from . import views

urlpatterns = [
    path('payment-processing/', views.payment_processing, name='payment-processing'),
]
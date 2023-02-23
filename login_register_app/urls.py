from django.urls import path
from . import views

urlpatterns = [
    path('create-login/', views.create_login, name='create_login'),
    path('verify-credentials/', views.verify_credentials, name='verify_credentials'),
    path('core-details/', views.core_details, name='core_details'),
    path('athlete-details/', views.athlete_details, name='athlete_details')
]

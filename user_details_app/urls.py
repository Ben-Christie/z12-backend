from django.urls import path
from . import views

urlpatterns = [
    path('core-details/', views.core_details, name='core_details'),
    path('athlete-details/', views.athlete_details, name='athlete_details'),
    path('personal-bests/', views.personal_bests, name='personal_bests'),
]
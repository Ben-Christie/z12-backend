from django.urls import path
from . import views

urlpatterns = [
    path('add-erg-metric/', views.add_erg_metric, name='add_erg_metric'),
    path('add-s-and-c-metric/', views.add_s_and_c_metric, name='add_s_and_c_metric'),
]

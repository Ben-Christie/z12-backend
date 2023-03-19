from django.urls import path
from . import views

urlpatterns = [
    path('populate-erg-analysis-chart/', views.populate_erg_chart, name='populate-erg-analysis-chart'),
    path('populate-s-and-c-analysis-chart/', views.populate_s_and_c_chart, name='populate-s-and-c-analysis-chart'),
]
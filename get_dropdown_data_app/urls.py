from django.urls import path
from . import views

urlpatterns = [
    path('club-names/', views.get_club_names, name='get_club_names'),
    path('race-categories/', views.get_race_category_names, name='get_race_categories'),
    path('coach-names/', views.get_coach_names, name='get_coach_names'),
]
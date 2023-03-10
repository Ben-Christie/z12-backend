from django.urls import path
from . import views

urlpatterns = [
    path('get-user-details/', views.get_user_details, name='get_user_details'),
    path('get-user-profile-picture/', views.get_user_picture, name='get_user_profile_picture'),
]
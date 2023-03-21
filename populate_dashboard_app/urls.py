from django.urls import path
from . import views

urlpatterns = [
    path('get-user-details/', views.get_user_details, name='get_user_details'),
    path('get-user-profile-picture/', views.get_user_picture, name='get_user_profile_picture'),
    path('get-personal-bests/', views.get_personal_bests, name='get_personal_bests'),
    path('calculate-pb-rating/', views.calculate_pb_rating, name='calculate_pb_rating'),
    path('populate-details-modal/', views.populate_details_modal, name='populate_details_modal'),
]
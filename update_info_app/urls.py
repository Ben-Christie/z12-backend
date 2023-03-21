from django.urls import path
from . import views

urlpatterns = [
    path('update-pb/', views.update_pb, name='update_pb'),
    path('update-user-details/', views.update_user_details, name='update_user_details'),
]

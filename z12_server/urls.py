"""z12_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login-register/', include('login_register_app.urls')),
    path('get-data/', include('get_dropdown_data_app.urls')),
    path('add-user-details/', include('user_details_app.urls')),
    path('payments/', include('payment_processing_app.urls')),
    path('gather-metrics/', include('metric_gathering_app.urls')),
    path('populate-dashboard/', include('populate_dashboard_app.urls')),
    path('chart-data/', include('chart_data_app.urls')),
    path('update-info/', include('update_info_app.urls')),
]

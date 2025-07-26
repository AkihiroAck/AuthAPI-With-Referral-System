"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from .views import PhoneAuthView, VerifyCodeView, ProfileView, register_page, verify_page, profile_page

urlpatterns = [
    path('api/phone/', PhoneAuthView.as_view(), name='phone_auth'),
    path('api/verify/', VerifyCodeView.as_view(), name='verify_code'),
    path('api/profile/<int:user_id>/', ProfileView.as_view(), name='profile'),
    path('register/', register_page, name='register_page'),
    path('login/', verify_page, name='verify_page'),
    path('profile/', profile_page, name='profile_page'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccountView.as_view(), name='account'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoanView.as_view(), name='loan'),
]
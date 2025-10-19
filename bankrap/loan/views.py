from django.urls import path
from . import views

app_name = 'loan'

urlpatterns = [
    path('', views.LoanView.as_view(), name='loan'),
    path('list/', views.LoanListView.as_view(), name='loan_list'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AccountView.as_view(), name='account'),
path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]

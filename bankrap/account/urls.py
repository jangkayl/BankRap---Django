from django.urls import path
from . import views

urlpatterns = [
path('', views.AccountView.as_view(), name='account'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    # Add these new messaging URLs:
    path('messages/new-messages/', views.get_new_messages, name='get_new_messages'),
    path('messages/start/<int:user_id>/', views.start_conversation, name='start_conversation')
]

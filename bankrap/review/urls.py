# reviews/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.reviews_view, name='reviews'),  # Changed from ReviewView.as_view()
    path('create/<int:loan_id>/', views.create_review, name='create_review'),
    path('edit/<int:review_id>/', views.edit_review_view, name='edit_review'),
    path('update/<int:review_id>/', views.update_review, name='update_review'),
    path('delete/<int:review_id>/', views.delete_review, name='delete_review'),
]
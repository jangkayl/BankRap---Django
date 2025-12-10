from django.contrib import admin
from django.urls import path
from bankrap import views as global_views
from account import views as account_views
from wallet import views as wallet_views
from loan import views as loan_views
from transaction import views as transaction_views
from review import views as review_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', global_views.index_view, name='index'),
    path('login/', account_views.login_view, name='login'),
    path('register/', account_views.register_view, name='register'),
    path('logout/', account_views.logout_view, name='logout'),

    path('dashboard/', account_views.dashboard_view, name='dashboard'),
    path('profile/', account_views.profile_view, name='profile'),

    path('wallet/', wallet_views.wallet_view, name='wallet'),
    path('wallet/add/', wallet_views.add_funds, name='add_funds'),
    path('wallet/withdraw/', wallet_views.withdraw_funds, name='withdraw_funds'),

    # Marketplace (Smart redirect for borrowers)
    path('loans/', loan_views.loan_marketplace, name='loan_list'),
    path('loans/market/', loan_views.loan_marketplace, name='loan_marketplace'),

    # Borrower specific
    path('loans/my-requests/', loan_views.my_loan_requests, name='my_loan_requests'),
    path('loans/create/', loan_views.create_loan_request, name='loan_create'),

    # Detail & Offers
    path('loans/<int:loan_id>/', loan_views.loan_detail, name='loan_detail'),
    path('loans/<int:loan_id>/offer/', loan_views.create_offer, name='loan_offer_create'),

    path('offers/', loan_views.loan_offer_list, name='offer_list'),
    path('repayments/', loan_views.repayment_schedule, name='repayment_schedule'),
    path('transactions/', transaction_views.transaction_history, name='transaction_history'),

    # NEW URL
    path('reviews/', review_views.reviews_view, name='reviews'),

    path('messages/', account_views.messaging_view, name='messaging'),

    path('settings/', account_views.settings_view, name='settings'),

    path('notifications/', account_views.notifications_view, name='notifications'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
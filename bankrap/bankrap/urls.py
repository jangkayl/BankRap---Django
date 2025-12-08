from django.contrib import admin
from django.urls import path
from bankrap import views as global_views  # if index_view is here
from account import views as account_views  # Import the new views we just made

urlpatterns = [
    path('admin/', admin.site.urls),

    # Global Pages (Home)
    path('', global_views.index_view, name='index'),

    # Auth Pages (Handled by Account App)
    path('login/', account_views.login_view, name='login'),
    path('register/', account_views.register_view, name='register'),
    path('logout/', account_views.logout_view, name='logout'),

    # App Features
    path('dashboard/', account_views.dashboard_view, name='dashboard'),

    # Wallet (Placeholder pointing to dashboard for now, or create wallet_view)
    path('wallet/', account_views.dashboard_view, name='wallet'),
]
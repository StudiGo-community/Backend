from django.urls import URLPattern, URLResolver, path

from apps.accounts.views.auth_views import LoginView, LogoutAPIView, TokenRefreshAPIView
from apps.accounts.views.check_email_views import CheckEmailView

urlpatterns: list[URLPattern | URLResolver] = [
    path("auth/login", LoginView.as_view(), name="auth_login"),
    path("auth/refresh", TokenRefreshAPIView.as_view(), name="auth_refresh"),
    path("auth/logout", LogoutAPIView.as_view(), name="auth_logout"),
    path("auth/check-email", CheckEmailView.as_view(), name="auth_check_email"),
]

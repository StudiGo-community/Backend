from django.urls import URLPattern, URLResolver, path

from apps.accounts.views.auth_views import LoginView, LogoutAPIView, TokenRefreshAPIView

urlpatterns: list[URLPattern | URLResolver] = [
    path("auth/login", LoginView.as_view(), name="auth_login"),
    path("auth/refresh", TokenRefreshAPIView.as_view(), name="auth_refresh"),
    path("auth/logout", LogoutAPIView.as_view(), name="auth_logout"),
]

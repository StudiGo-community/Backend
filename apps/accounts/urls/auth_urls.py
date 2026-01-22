from django.urls import URLPattern, URLResolver, path

from apps.accounts.views.auth_views import LoginView

urlpatterns: list[URLPattern | URLResolver] = [
    path("auth/login", LoginView.as_view(), name="email_login"),
]

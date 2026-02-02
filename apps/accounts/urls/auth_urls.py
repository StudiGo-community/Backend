from django.urls import URLPattern, URLResolver, path

from apps.accounts.views.auth_views import LoginView, LogoutAPIView, TokenRefreshAPIView
from apps.accounts.views.check_views import CheckEmailView, CheckNicknameView
from apps.accounts.views.email_verification_views import (
    ResetPasswordEmailConfirmCodeView,
    ResetPasswordEmailSendCodeView,
    SignupEmailConfirmCodeView,
    SignupEmailSendCodeView,
)
from apps.accounts.views.find_email_views import FindEmailView
from apps.accounts.views.reset_password_views import PasswordResetView
from apps.accounts.views.signup_views import EmailSignupView
from apps.accounts.views.withdrawal_views import (
    WithdrawalIssueTokenByPasswordView,
    WithdrawalTokenMethodView,
    WithdrawalView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("auth/login", LoginView.as_view(), name="auth_login"),
    path("auth/refresh", TokenRefreshAPIView.as_view(), name="auth_refresh"),
    path("auth/logout", LogoutAPIView.as_view(), name="auth_logout"),
    path("auth/check-email", CheckEmailView.as_view(), name="auth_check_email"),
    path(
        "auth/check-nickname", CheckNicknameView.as_view(), name="auth_check_nickname"
    ),
    path(
        "auth/email-verification/signup/send-code",
        SignupEmailSendCodeView.as_view(),
        name="email_verification_signup_send_code",
    ),
    path(
        "auth/email-verification/signup/confirm-code",
        SignupEmailConfirmCodeView.as_view(),
        name="email_verification_signup_confirm_code",
    ),
    path(
        "auth/email-verification/reset-password/send-code",
        ResetPasswordEmailSendCodeView.as_view(),
        name="email_verification_reset_password_send_code",
    ),
    path(
        "auth/email-verification/reset-password/confirm-code",
        ResetPasswordEmailConfirmCodeView.as_view(),
        name="email_verification_reset_password_confirm_code",
    ),
    path("auth/signup/email", EmailSignupView.as_view(), name="auth_signup_email"),
    path("auth/withdrawal-token", WithdrawalTokenMethodView.as_view()),
    path(
        "auth/withdrawal-token/password", WithdrawalIssueTokenByPasswordView.as_view()
    ),
    path("auth/withdrawal", WithdrawalView.as_view(), name="auth_withdrawal"),
    path("auth/find-email", FindEmailView.as_view(), name="find-email"),
    path("auth/password-reset", PasswordResetView.as_view()),
]

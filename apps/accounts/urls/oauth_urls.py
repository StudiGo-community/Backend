from django.urls import path

from apps.accounts.views.oauth_callback_views import (
    GoogleCallbackView,
    KakaoCallbackView,
)
from apps.accounts.views.oauth_login_views import (
    GoogleLoginView,
    KakaoLoginView,
)
from apps.accounts.views.oauth_signup_views import (
    SocialLinkConfirmView,
    SocialSignupCompleteView,
)

urlpatterns = [
    # OAuth login
    path("oauth/google/login/", GoogleLoginView.as_view()),
    path("oauth/kakao/login/", KakaoLoginView.as_view()),
    # OAuth callback (JSON)
    path("oauth/google/callback/", GoogleCallbackView.as_view()),
    path("oauth/kakao/callback/", KakaoCallbackView.as_view()),
    # OAuth Signup
    path("oauth/social-signup/complete", SocialSignupCompleteView.as_view()),
    path("oauth/social-link/confirm", SocialLinkConfirmView.as_view()),
]

# Base
# 회원가입/로그인/로그아웃
from apps.accounts.serializers.auth_serializers import (
    LoginRequestSerializer,
    LoginResponseSerializer,
    TokenPayloadSerializer,
)
from apps.accounts.serializers.base import BaseMixin

# 이메일 인증코드 발송/확인
from apps.accounts.serializers.email_verification_serializers import (
    EmailConfirmCodeRequestSerializer,
    EmailConfirmCodeResponseSerializer,
    EmailSendCodeResponseSerializer,
    ResetPasswordEmailSendCodeRequestSerializer,
    SignupEmailSendCodeRequestSerializer,
)

# 소셜 로그인
from apps.accounts.serializers.oauth_serializers import (
    SocialLinkConfirmRequestSerializer,
    SocialSignupCompleteRequestSerializer,
)

# 비밀번호 찾기/재설정
from apps.accounts.serializers.password_serializers import (
    PasswordChangeResponseSerializer,
    PasswordChangeSerializer,
    PasswordResetResponseSerializer,
    PasswordResetSendCodeResponseSerializer,
    PasswordResetSendCodeSerializer,
    PasswordResetSerializer,
    PasswordResetVerifyCodeResponseSerializer,
    PasswordResetVerifyCodeSerializer,
)

# 이메일 찾기 (나중에)

# 프로필 (마이페이지) (나중에)

__all__ = [
    # Base
    "BaseMixin",
    # 이메일 인증코드 발송/확인
    "ResetPasswordEmailSendCodeRequestSerializer",
    "SignupEmailSendCodeRequestSerializer",
    "EmailSendCodeResponseSerializer",
    "EmailConfirmCodeRequestSerializer",
    "EmailConfirmCodeResponseSerializer",
    # 로그인
    "TokenPayloadSerializer",
    "LoginRequestSerializer",
    "LoginResponseSerializer",
    # 소셜 로그인
    "KakaoOAuthSerializer",
    "GoogleOAuthSerializer",
    "OAuthResponseSerializer",
    "KakaoProfileSerializer",
    "GoogleProfileSerializer",
    "SocialSignupCompleteSerializer",
    "SocialSignupCompleteResponseSerializer",
    # 비밀번호 찾기/재설정
    "PasswordResetSendCodeSerializer",
    "PasswordResetSendCodeResponseSerializer",
    "PasswordResetVerifyCodeSerializer",
    "PasswordResetVerifyCodeResponseSerializer",
    "PasswordResetSerializer",
    "PasswordResetResponseSerializer",
    "PasswordChangeSerializer",
    "PasswordChangeResponseSerializer",
]

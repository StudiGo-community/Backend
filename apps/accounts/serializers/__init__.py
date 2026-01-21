# Base
# 회원가입/로그인/로그아웃
from apps.accounts.serializers.auth.__init__ import (
    EmailCheckResponseSerializer,
    EmailCheckSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    LogoutResponseSerializer,
    LogoutSerializer,
    NicknameCheckResponseSerializer,
    NicknameCheckSerializer,
    SignupResponseSerializer,
    SignupSerializer,
    TokenRefreshResponseSerializer,
    TokenRefreshSerializer,
)
from apps.accounts.serializers.base import BaseMixin

# 소셜 로그인
from apps.accounts.serializers.oauth_serializers import (
    GoogleOAuthSerializer,
    GoogleProfileSerializer,
    KakaoOAuthSerializer,
    KakaoProfileSerializer,
    OAuthResponseSerializer,
    SocialSignupCompleteResponseSerializer,
    SocialSignupCompleteSerializer,
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

# 인증코드 발송/확인
from apps.accounts.serializers.verification_serializers import (
    EmailSendCodeSerializer,
    EmailVerifyCodeSerializer,
    EmailVerifyResponseSerializer,
    PhoneSendCodeSerializer,
    PhoneVerifyCodeSerializer,
    PhoneVerifyResponseSerializer,
)

# 이메일 찾기 (나중에)

# 프로필 (마이페이지) (나중에)

__all__ = [
    # Base
    "BaseMixin",
    # 인증코드 발송/확인
    "EmailSendCodeSerializer",
    "EmailVerifyCodeSerializer",
    "EmailVerifyResponseSerializer",
    "PhoneSendCodeSerializer",
    "PhoneVerifyCodeSerializer",
    "PhoneVerifyResponseSerializer",
    # 회원가입/로그인/로그아웃
    "EmailCheckSerializer",
    "EmailCheckResponseSerializer",
    "NicknameCheckSerializer",
    "NicknameCheckResponseSerializer",
    "SignupSerializer",
    "SignupResponseSerializer",
    "LoginSerializer",
    "LoginResponseSerializer",
    "TokenRefreshSerializer",
    "TokenRefreshResponseSerializer",
    "LogoutSerializer",
    "LogoutResponseSerializer",
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

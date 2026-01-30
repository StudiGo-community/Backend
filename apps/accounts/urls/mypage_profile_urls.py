from django.urls import path

from apps.accounts.views.mypage_profile_views import (
    PasswordChangeView,
    ProfileImageView,
    ProfileView,
)

urlpatterns = [
    # 프로필 조회 및 수정
    path("api/v1/users/me/profile", ProfileView.as_view(), name="profile"),
    # 프로필 이미지 업로드
    path(
        "api/v1/users/me/profile/image",
        ProfileImageView.as_view(),
        name="profile-image",
    ),
    # 비밀번호 변경
    path(
        "api/v1/users/me/profile/password",
        PasswordChangeView.as_view(),
        name="password-change",
    ),
]

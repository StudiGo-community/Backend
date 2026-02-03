from django.urls import URLPattern, URLResolver, path

from apps.accounts.views.mypage_profile_views import (
    PasswordChangeView,
    ProfileImageView,
    ProfileView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    # 프로필 조회 및 수정
    path("me/profile", ProfileView.as_view(), name="profile"),
    # 프로필 이미지 업로드
    path(
        "me/profile/image",
        ProfileImageView.as_view(),
        name="profile-image",
    ),
    # 비밀번호 변경
    path(
        "me/profile/password",
        PasswordChangeView.as_view(),
        name="password-change",
    ),
]

from django.urls import path

from apps.chat.views.admin_message_view import AdminMessageDeleteAPIView
from apps.chat.views.ban_view import AdminBanListCreateAPIView, AdminBanUpdateAPIView

urlpatterns = [
    # 관리자 메세지 삭제
    path(
        "chat/<int:room_id>/messages/<int:message_id>",
        AdminMessageDeleteAPIView.as_view(),
    ),
    # 관리자 벤 리스트
    path("chat/bans", AdminBanListCreateAPIView.as_view()),
    # 관리자 벤 수정
    path("chat/bans/<int:ban_id>", AdminBanUpdateAPIView.as_view()),
]

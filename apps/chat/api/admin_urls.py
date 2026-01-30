from django.urls import path

from apps.chat.views.admin_message_view import AdminMessageDeleteAPIView

urlpatterns = [
    path(
        "admin/chat/<int:room_id>/messages/<int:message_id>/",
        AdminMessageDeleteAPIView.as_view(),
    ),
]

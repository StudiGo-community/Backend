from django.urls import path

from apps.community.views.post_report_views import PostReportCreateAPIView
from apps.community.views.comment_report_views import CommentReportCreateAPIView

urlpatterns = [
    path(
        "posts/<int:post_id>/reports",
        PostReportCreateAPIView.as_view(),
    ),
    path(
        "posts/<int:post_id>/comments/<int:comment_id>/reports",
        CommentReportCreateAPIView.as_view(),
    ),
]
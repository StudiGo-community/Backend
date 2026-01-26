from __future__ import annotations

from typing import Any, Dict

from rest_framework import serializers

from apps.community.models.post_reports import PostReport
from apps.community.models.comment_reports import CommentReport
from apps.core.enumeration.community_enumerations import ReportStatus


class ReportCreateSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=100)

    def validate_reason(self, value: str) -> str:
        reason = value.strip()
        if not reason:
            raise serializers.ValidationError("신고 사유는 필수입니다.")
        return reason


class PostReportResponseSerializer(serializers.Serializer):
    report_id = serializers.IntegerField()
    post_id = serializers.IntegerField()
    reason = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    @staticmethod
    def from_instance(report: PostReport) -> Dict[str, Any]:
        status_value = (
            "RECEIVED" if report.status == ReportStatus.PENDING else report.status
        )
        return {
            "report_id": report.id,
            "post_id": report.post_id,
            "reason": report.reason,
            "status": status_value,
            "created_at": report.created_at,
        }


class CommentReportResponseSerializer(serializers.Serializer):
    report_id = serializers.IntegerField()
    comment_id = serializers.IntegerField()
    reason = serializers.CharField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()

    @staticmethod
    def from_instance(report: CommentReport) -> Dict[str, Any]:
        status_value = (
            "RECEIVED" if report.status == ReportStatus.PENDING else report.status
        )
        return {
            "report_id": report.id,
            "comment_id": report.comment_id,
            "reason": report.reason,
            "status": status_value,
            "created_at": report.created_at,
        }
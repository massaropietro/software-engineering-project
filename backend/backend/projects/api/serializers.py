from rest_framework import serializers

from backend.core.api.serializers import BaseModelSerializer
from backend.projects.models import MutationAnalysis, MutationResult, Project


class ProjectSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "zip_file",
            "repo_url",
            "status",
            "created",
            "file_structure",
            "secret_token",
        ]
        read_only_fields = ["status", "created", "file_structure", "secret_token"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        if request and request.method != 'POST':
            data.pop('secret_token', None)

        return data


class MutationAnalysisSerializer(BaseModelSerializer):
    class Meta:
        model = MutationAnalysis
        fields = [
            "id",
            "project",
            "files",
            "language",
            "score",
            "status",
            "raw_output",
            "created",
            "modified",
        ]
        read_only_fields = ["id", "score", "status", "raw_output", "created", "modified"]

    def validate_project(self, value):
        if value.status == Project.STATUS.filesystem_build_failed:
            raise serializers.ValidationError(
                "Cannot start analysis on a project with failed filesystem build."
            )
        return value


class MutationResultSerializer(BaseModelSerializer):
    class Meta:
        model = MutationResult
        fields = [
            "id",
            "analysis",
            "file",
            "mutant_id",
            "status",
            "is_equivalent",
            "line",
            "description",
            "created",
        ]
        read_only_fields = ["id", "created", "is_equivalent"]

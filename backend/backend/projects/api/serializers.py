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
        request = self.context.get("request")

        if request and request.method != "POST":
            data.pop("secret_token", None)

        return data


class MutationAnalysisSerializer(BaseModelSerializer):
    # Campo aggiunto per ricevere il token dal payload senza salvarlo nel DB per questo modello
    secret_token = serializers.CharField(write_only=True, required=True)

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
            "secret_token",
        ]
        read_only_fields = [
            "id",
            "score",
            "status",
            "raw_output",
            "created",
            "modified",
        ]

    def validate(self, attrs):
        project = attrs.get("project")
        # Estraiamo il token dal payload (lo rimuoviamo così non tenta di salvarlo nel db model)
        secret_token = attrs.pop("secret_token", None)

        if project and secret_token:
            if str(project.secret_token) != secret_token:
                raise serializers.ValidationError(
                    {"secret_token": "Token di progetto non valido o errato."}
                )

        if project and project.status == Project.STATUS.filesystem_build_failed:
            raise serializers.ValidationError(
                {
                    "project": "Cannot start analysis on a project with failed filesystem build."
                }
            )
        return attrs


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

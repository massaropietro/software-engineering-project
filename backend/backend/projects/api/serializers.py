from backend.projects.models import Project
from backend.core.api.serializers import BaseModelSerializer


class ProjectSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "zip_file",
            "repo_url",
            "status",
            "created",
        ]
        read_only_fields = ["status", "created"]

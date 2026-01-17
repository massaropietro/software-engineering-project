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
            "file_structure",
        ]
        read_only_fields = ["status", "created", "file_structure"]

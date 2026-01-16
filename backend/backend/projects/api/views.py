from rest_framework import viewsets

from backend.projects.api.serializers import ProjectSerializer
from backend.projects.models import Project


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

from rest_framework import viewsets
from rest_framework import mixins

from backend.projects.api.serializers import ProjectSerializer, ProjectFileSerializer
from backend.projects.models import Project


from backend.projects.models import ProjectFile


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectFileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer

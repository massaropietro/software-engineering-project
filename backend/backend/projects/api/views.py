from rest_framework import viewsets
from rest_framework import mixins

from backend.projects.api.serializers import ProjectSerializer, ProjectFileSerializer
from backend.projects.models import Project


from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from backend.projects.models import ProjectFile


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class ProjectFileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer

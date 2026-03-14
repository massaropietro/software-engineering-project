from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from backend.projects.tasks import build_filesystem_task

from backend.projects.api.serializers import ProjectSerializer, ProjectFileSerializer
from backend.projects.models import Project


from backend.projects.models import ProjectFile


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(detail=True, methods=["post"])
    def retry_build_filesystem(self, request, pk=None):
        project = self.get_object()
        # We might want to restrict this to only failed projects, but for now let's allow it
        # or check generic failure status.
        # if project.status not in [Project.STATUS.filesystem_build_failed, Project.STATUS.failed]:
        #     return Response({"detail": "Project is not in a failed state"}, status=status.HTTP_400_BAD_REQUEST)

        build_filesystem_task.delay(project.id)
        return Response({"status": "Build retry started"})


class ProjectFileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = ProjectFile.objects.all()
    serializer_class = ProjectFileSerializer

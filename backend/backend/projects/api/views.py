from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from backend.projects.api.serializers import (
    MutationAnalysisSerializer,
    MutationResultSerializer,
    ProjectSerializer,
)
from backend.projects.models import MutationAnalysis, MutationResult, Project
from backend.projects.tasks import build_filesystem_task, run_mutation_analysis_task
from backend.projects.services import get_mutant_diff


def verify_project_token(request, project):
    """
    Verifica che l'header 'X-Project-Token' corrisponda al token segreto del progetto.
    """
    token = request.headers.get("X-Project-Token")
    if not token or str(project.secret_token) != token:
        raise PermissionDenied("Token di progetto mancante o non valido. Azione non autorizzata.")


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @action(detail=True, methods=["post"], url_path="retry_build_filesystem", url_name="retry-build-filesystem")
    def retry_build_filesystem(self, request, pk=None):
        project = self.get_object()
        verify_project_token(request, project)

        build_filesystem_task.delay(project.id)
        return Response({"status": "Build retry started"})

    @action(detail=True, methods=["get"], url_path="file_content", url_name="file-content")
    def file_content(self, request, pk=None):
        project = self.get_object()
        file_path = request.query_params.get("path")

        if not file_path:
            return Response({"detail": "Query parameter 'path' is required."}, status=status.HTTP_400_BAD_REQUEST)

        from backend.projects.services import get_file_content_from_source

        try:
            content = get_file_content_from_source(project, file_path)
            return Response({"content": content})
        except ValueError:
            return Response({"detail": "Invalid file path."}, status=status.HTTP_400_BAD_REQUEST)
        except FileNotFoundError:
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)


class MutationAnalysisViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = MutationAnalysis.objects.select_related("project").all()
    serializer_class = MutationAnalysisSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = serializer.validated_data['project']
        verify_project_token(request, project)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        analysis = serializer.save()
        run_mutation_analysis_task.delay(str(analysis.id))

    @action(detail=True, methods=["post"], url_path="retry", url_name="retry")
    def retry(self, request, pk=None):
        analysis = self.get_object()
        verify_project_token(request, analysis.project)

        if analysis.status == MutationAnalysis.STATUS.running:
            return Response(
                {"detail": "Cannot retry an analysis that is currently running."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Clear previous results and reset status
        analysis.mutants.all().delete()
        analysis.status = MutationAnalysis.STATUS.pending
        analysis.score = None
        analysis.raw_output = None
        analysis.save()

        run_mutation_analysis_task.delay(str(analysis.id))
        return Response({"status": "Retry started"})

    @action(detail=True, methods=["get"], url_path="stats", url_name="stats")
    def stats(self, request, pk=None):
        analysis = self.get_object()
        from django.db.models import Count

        counts = analysis.mutants.values("status").annotate(count=Count("status"))
        stats_dict = {item["status"]: item["count"] for item in counts}

        return Response({
            "total": sum(stats_dict.values()),
            "score": analysis.score,
            "status": analysis.status,
            "breakdown": stats_dict
        })

    @action(detail=False, methods=["get"], url_path=r"(?P<secret_token>[^/.]+)/project", url_name="project-by-token")
    def project_by_token(self, request, secret_token=None):
        project = get_object_or_404(Project, secret_token=secret_token)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

class MutationResultViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = MutationResult.objects.select_related("analysis").all()
    serializer_class = MutationResultSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        analysis_id = self.request.query_params.get("analysis")
        if analysis_id:
            qs = qs.filter(analysis_id=analysis_id)

        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        file_param = self.request.query_params.get("file")
        if file_param:
            qs = qs.filter(file__icontains=file_param)

        return qs

    @action(detail=True, methods=["get"], url_path="diff", url_name="diff")
    def diff(self, request, pk=None):
        mutant = self.get_object()
        try:
            diff_content = get_mutant_diff(mutant)
            return Response({"diff": diff_content})
        except Exception as e:
            return Response(
                {"detail": f"Error generating diff: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

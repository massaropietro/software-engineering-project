from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

from backend.projects.api.views import (
    MutationAnalysisViewSet,
    MutationResultViewSet,
    ProjectViewSet,
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("projects", ProjectViewSet, basename="projects")
router.register("analyses", MutationAnalysisViewSet, basename="analyses")
router.register("mutation-results", MutationResultViewSet, basename="mutation-results")

app_name = "api"
urlpatterns = [
    path("", include(router.urls)),
    path("", include("backend.core.api.urls")),
]

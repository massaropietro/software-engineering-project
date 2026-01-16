from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from backend.projects.api.views import ProjectViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("projects", ProjectViewSet, basename="projects")

app_name = "api"
urlpatterns = [
    path("", include(router.urls)),
    path("", include("backend.core.api.urls")),
]

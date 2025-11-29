from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

app_name = "api"
urlpatterns = [
    path("", include(router.urls)),
    path("", include("backend.core.api.urls")),
]

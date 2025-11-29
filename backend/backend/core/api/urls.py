from django.urls import path

from .views import HealthCheckAPIView
from .views import ReadinessCheckAPIView

urlpatterns = [
    path("health/", HealthCheckAPIView.as_view(), name="health-check"),
    path("readiness/", ReadinessCheckAPIView.as_view(), name="readiness-check"),
]

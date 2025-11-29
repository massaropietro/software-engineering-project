from django.urls import resolve
from django.urls import reverse

from backend.core.api.views import HealthCheckAPIView
from backend.core.api.views import ReadinessCheckAPIView


def test_health_url_resolves():
    url = reverse("api:health-check")
    assert resolve(url).func.view_class == HealthCheckAPIView


def test_readiness_url_resolves():
    url = reverse("api:readiness-check")
    assert resolve(url).func.view_class == ReadinessCheckAPIView

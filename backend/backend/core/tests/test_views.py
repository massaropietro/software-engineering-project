import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestHealthCheckAPIView:
    def test_health_check_returns_200(self, api_client):
        url = reverse("api:health-check")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}


@pytest.mark.django_db
class TestReadinessCheckAPIView:
    def test_readiness_check_success(self, api_client):
        url = reverse("api:readiness-check")
        response = api_client.get(url)
        data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert data["ready"] is True
        assert all(data["checks"].values())

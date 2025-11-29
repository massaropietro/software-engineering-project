import tempfile
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckAPIView(APIView):
    """Health check endpoint."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "healthy"})


class ReadinessCheckAPIView(APIView):
    """Readiness check completo con più controlli"""

    permission_classes = [AllowAny]

    def get(self, request):
        checks = {}

        # --- 1. Database ---
        checks["database"] = self.check_database()

        # --- 2. Redis cache ---
        checks["cache"] = self.check_cache()

        # --- 3. Filesystem ---
        checks["filesystem"] = self.check_filesystem()

        # Stato complessivo
        all_ready = all(checks.values())
        status_code = (
            status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(
            {
                "debug_mode": settings.DEBUG,
                "ready": all_ready,
                "checks": checks,
            },
            status=status_code,
        )

    # --- Funzioni di check modulari ---
    @staticmethod
    def check_database():
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception:
            return False
        else:
            return True

    @staticmethod
    def check_cache():
        try:
            cache.set("health_check", "ok", 5)
            return cache.get("health_check") == "ok"
        except Exception:
            return False

    @staticmethod
    def check_filesystem():
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            test_file = tmp_path / "health_check.txt"

            try:
                test_file.write_text("ok")
                value = test_file.read_text()
            except Exception:
                return False
            else:
                return value == "ok"

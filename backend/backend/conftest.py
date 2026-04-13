import pytest
import shutil
from pathlib import Path
from django.conf import settings
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(autouse=True)
def cleanup_media_projects():
    yield
    # Cleanup project sources in the test media root
    projects_dir = Path(settings.MEDIA_ROOT) / "_projects_sources"
    if projects_dir.exists():
        shutil.rmtree(projects_dir)

import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch

from backend.projects.models import MutationAnalysis, MutationResult
from backend.projects.tests.factories import ProjectFactory, MutationAnalysisFactory

pytestmark = pytest.mark.django_db


def test_create_mutation_analysis(client):
    project = ProjectFactory(status="filesystem_created")

    url = reverse("api:analyses-list")
    data = {
        "project": project.id,
        "files": ["main.py", "utils.py"],
        "language": "python",
    }

    # Mock the celery task
    with patch("backend.projects.tasks.run_mutation_analysis_task.delay") as mock_task:
        response = client.post(url, data, content_type="application/json")

        assert response.status_code == status.HTTP_201_CREATED
        assert MutationAnalysis.objects.count() == 1
        analysis = MutationAnalysis.objects.first()
        assert analysis.project == project
        assert analysis.language == "python"
        assert analysis.status == "pending"
        assert len(analysis.files) == 2

        mock_task.assert_called_once_with(str(analysis.id))


def test_list_mutation_results(client):
    analysis = MutationAnalysisFactory(status="completed")
    MutationResult.objects.create(
        analysis=analysis,
        file="main.py",
        mutant_id="1",
        status="killed",
    )

    url = reverse("api:mutation-results-list")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["mutant_id"] == "1"
    assert response.data["results"][0]["status"] == "killed"


def test_list_analyses_filtered_by_project(client):
    project = ProjectFactory()
    MutationAnalysisFactory(project=project)
    MutationAnalysisFactory() # different project
    
    url = reverse("api:analyses-list")
    response = client.get(f"{url}?project={project.id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["project"] == project.id


def test_list_results_filtered_by_analysis(client):
    analysis = MutationAnalysisFactory()
    MutationResult.objects.create(analysis=analysis, file="a.py", mutant_id="1", status="killed")
    
    analysis2 = MutationAnalysisFactory()
    MutationResult.objects.create(analysis=analysis2, file="b.py", mutant_id="1", status="survived")
    
    url = reverse("api:mutation-results-list")
    response = client.get(f"{url}?analysis={analysis.id}")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["file"] == "a.py"


def test_retry_mutation_analysis_success(client):
    analysis = MutationAnalysisFactory(status="failed")

    MutationResult.objects.create(
        analysis=analysis,
        file="main.py",
        mutant_id="1",
        status="timeout",
    )

    url = reverse("api:analyses-retry", args=[analysis.id])
    with patch("backend.projects.tasks.run_mutation_analysis_task.delay") as mock_task:
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        analysis.refresh_from_db()
        assert analysis.status == "pending"
        assert analysis.mutants.count() == 0  # old results should be clear
        mock_task.assert_called_once_with(str(analysis.id))


def test_retry_mutation_analysis_fails_if_running(client):
    analysis = MutationAnalysisFactory(status="running")

    url = reverse("api:analyses-retry", args=[analysis.id])
    response = client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.data or "non_field_errors" in response.data

def test_list_analyses_filtered_by_status(client):
    MutationAnalysisFactory(status="completed")
    MutationAnalysisFactory(status="failed")
    
    url = reverse("api:analyses-list")
    response = client.get(f"{url}?status=completed")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["status"] == "completed"

def test_list_results_filtered_by_status(client):
    analysis = MutationAnalysisFactory()
    MutationResult.objects.create(analysis=analysis, file="a.py", mutant_id="1", status="killed")
    MutationResult.objects.create(analysis=analysis, file="b.py", mutant_id="2", status="survived")
    
    url = reverse("api:mutation-results-list")
    response = client.get(f"{url}?status=killed")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["status"] == "killed"

def test_list_results_filtered_by_file(client):
    analysis = MutationAnalysisFactory()
    MutationResult.objects.create(analysis=analysis, file="core/logic.py", mutant_id="1", status="killed")
    MutationResult.objects.create(analysis=analysis, file="web/views.py", mutant_id="2", status="killed")
    
    url = reverse("api:mutation-results-list")
    response = client.get(f"{url}?file=core")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["file"] == "core/logic.py"
def test_create_mutation_analysis_fails_if_project_failed(client):
    project = ProjectFactory(status="filesystem_build_failed")
    
    url = reverse("api:analyses-list")
    data = {"project": project.id, "files": [], "language": "python"}
    
    response = client.post(url, data, content_type="application/json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot start analysis on a project with failed filesystem build." in str(response.data)


def test_create_mutation_analysis_succeeds_even_if_pending(client):
    # This is to verify that PENDING is NOT blocked by serializer, but handled by task auto-build
    project = ProjectFactory(status="pending")
    
    url = reverse("api:analyses-list")
    data = {"project": project.id, "files": [], "language": "python"}
    
    with patch("backend.projects.tasks.run_mutation_analysis_task.delay"):
        response = client.post(url, data, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED

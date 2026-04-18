import pytest
from unittest import mock
from backend.projects.models import Project
from backend.projects.tests.factories import ProjectFactory


@pytest.mark.django_db
class TestProjectViewSet:
    def test_list_projects(self, client):
        Project.objects.all().delete()
        ProjectFactory.create_batch(3)
        response = client.get("/api/projects/")
        assert response.status_code == 200
        data = response.data["results"] if "results" in response.data else response.data
        assert len(data) == 3

    def test_create_project_invalid(self, client):
        data = {"name": "New Project"}
        response = client.post("/api/projects/", data)

        assert response.status_code == 400
        assert "non_field_errors" in response.data or "detail" in response.data

    def test_create_project_valid_url(self, client):
        data = {"name": "URL Project", "repo_url": "http://example.com"}
        response = client.post("/api/projects/", data)
        assert response.status_code == 201
        assert Project.objects.filter(name="URL Project").exists()

    def test_retrieve_project(self, client):
        project = ProjectFactory(name="Retrieve Me", repo_url="http://retrieve.com")
        response = client.get(f"/api/projects/{project.pk}/")
        assert response.status_code == 200
        assert response.data["name"] == "Retrieve Me"

    def test_update_project(self, client):
        project = ProjectFactory(name="Old Name", repo_url="http://old.com")
        data = {
            "name": "New Name",
            "repo_url": "http://new.com",
        }
        response = client.put(
            f"/api/projects/{project.pk}/", data, content_type="application/json"
        )
        assert response.status_code == 200
        project.refresh_from_db()
        assert project.name == "New Name"
        assert project.repo_url == "http://new.com"

    def test_partial_update_project(self, client):
        project = ProjectFactory(name="Old Name", repo_url="http://old.com")
        data = {"name": "Patched Name"}
        response = client.patch(
            f"/api/projects/{project.pk}/", data, content_type="application/json"
        )
        assert response.status_code == 200
        project.refresh_from_db()
        assert project.name == "Patched Name"
        assert project.repo_url == "http://old.com"

    def test_delete_project(self, client):
        project = ProjectFactory()
        response = client.delete(f"/api/projects/{project.pk}/")
        assert response.status_code == 204
        assert not Project.objects.filter(pk=project.pk).exists()

    @mock.patch("backend.projects.api.views.build_filesystem_task")
    def test_retry_build_filesystem(self, mock_task, client):
        project = ProjectFactory(status="filesystem_build_failed")
        response = client.post(
            f"/api/projects/{project.pk}/retry_build_filesystem/",
            data={"secret_token": str(project.secret_token)},
            content_type="application/json"
        )

        assert response.status_code == 200
        assert mock_task.delay.called
        assert mock_task.delay.call_args == mock.call(project.pk)

    @mock.patch("backend.projects.services.get_file_content_from_source")
    def test_file_content_success(self, mock_get_content, client):
        project = ProjectFactory()
        mock_get_content.return_value = "file content"
        response = client.get(f"/api/projects/{project.pk}/file_content/?path=main.py")
        
        assert response.status_code == 200
        assert response.data["content"] == "file content"
        mock_get_content.assert_called_once_with(project, "main.py")

    def test_file_content_missing_path(self, client):
        project = ProjectFactory()
        response = client.get(f"/api/projects/{project.pk}/file_content/")
        assert response.status_code == 400
        assert "is required" in response.data["detail"]

    @mock.patch("backend.projects.services.get_file_content_from_source")
    def test_file_content_not_found(self, mock_get_content, client):
        project = ProjectFactory()
        mock_get_content.side_effect = FileNotFoundError()
        response = client.get(f"/api/projects/{project.pk}/file_content/?path=main.py")
        assert response.status_code == 404

    @mock.patch("backend.projects.services.get_file_content_from_source")
    def test_file_content_invalid_path(self, mock_get_content, client):
        project = ProjectFactory()
        mock_get_content.side_effect = ValueError()
        response = client.get(f"/api/projects/{project.pk}/file_content/?path=../passwd")
        assert response.status_code == 400

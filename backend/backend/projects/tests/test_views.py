import pytest
from backend.projects.models import Project
from backend.projects.tests.factories import ProjectFactory


@pytest.mark.django_db
class TestProjectViewSet:
    def test_list_projects(self, client):
        Project.objects.all().delete()
        ProjectFactory.create_batch(3)
        response = client.get("/api/projects/")
        assert response.status_code == 200
        # If pagination is enabled, response.data has 'results'. If not, it's a list.
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

    def test_delete_project(self, client):
        project = ProjectFactory()
        response = client.delete(f"/api/projects/{project.pk}/")
        assert response.status_code == 204
        assert not Project.objects.filter(pk=project.pk).exists()


@pytest.mark.django_db
class TestProjectFileViewSet:
    def test_retrieve_file(self, client):
        from backend.projects.tests.factories import ProjectFileFactory

        project_file = ProjectFileFactory(content="Content check")
        response = client.get(f"/api/files/{project_file.pk}/")
        assert response.status_code == 200
        assert response.data["content"] == "Content check"
        assert response.data["path"] == project_file.path

    def test_retrieve_file_not_found(self, client):
        import uuid

        response = client.get(f"/api/files/{uuid.uuid4()}/")
        assert response.status_code == 404

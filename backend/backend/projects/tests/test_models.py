import pytest
from django.core.exceptions import ValidationError
from backend.projects.models import Project, MutationAnalysis, MutationResult
from backend.projects.tests.factories import ProjectFactory


@pytest.mark.django_db
class TestProjectModel:
    def test_create_valid_project_with_url(self):
        project = ProjectFactory(repo_url="http://example.com", zip_file=None)
        project.full_clean()

        assert project.repo_url == "http://example.com"

    def test_create_valid_project_with_zip(self):
        project = ProjectFactory(repo_url="", zip_file="path/to/file.zip")
        project.full_clean()

        assert project.zip_file == "path/to/file.zip"

    def test_create_invalid_project_no_content(self):
        project = ProjectFactory.build(repo_url="", zip_file=None)
        with pytest.raises(ValidationError) as exc:
            project.full_clean()

        assert "You must provide either a zip file or a repository URL." in str(
            exc.value
        )

    def test_str_representation(self):
        project = ProjectFactory(name="Test Project", repo_url="http://test.com")
        assert str(project) == f"{project.name} ({project.status})"

    def test_mutation_analysis_str(self):
        project = ProjectFactory(name="Test Project")
        analysis = MutationAnalysis.objects.create(project=project, status="pending")
        assert str(analysis) == "Analysis(Test Project, pending)"

    def test_mutation_result_str(self):
        project = ProjectFactory(name="Test Project")
        analysis = MutationAnalysis.objects.create(project=project, status="completed")
        result = MutationResult.objects.create(
            analysis=analysis, file="test.py", mutant_id="123", status="killed"
        )
        assert str(result) == "Mutant #123 [killed] in test.py"

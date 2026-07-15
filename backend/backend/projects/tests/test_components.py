import pytest
from unittest import mock
from django.core.exceptions import ValidationError
from backend.projects.models import Project
from backend.projects.validators import ProjectValidator


@pytest.mark.django_db
def test_project_validator():
    validator = ProjectValidator()

    # Valid zip
    project_zip = Project(name="Zip", zip_file="test.zip")
    validator.validate(project_zip)  # Should not raise

    # Valid repo
    project_repo = Project(name="Repo", repo_url="https://github.com/foo/bar")
    validator.validate(project_repo)  # Should not raise

    # Invalid (neither)
    project_invalid = Project(name="Invalid")
    with pytest.raises(
        ValidationError, match="You must provide either a zip file or a repository URL."
    ):
        validator.validate(project_invalid)


@pytest.mark.django_db
def test_trigger_filesystem_build_signal():
    with mock.patch(
        "backend.projects.signals.build_filesystem_task.delay"
    ) as mock_task:
        # Should trigger on creation with STATUS.uploaded
        project = Project.objects.create(
            name="New Project",
            repo_url="https://github.com/foo/bar",
            status=Project.STATUS.uploaded,
        )
        mock_task.assert_called_once_with(project.id)

        mock_task.reset_mock()

        # Should NOT trigger if not STATUS.uploaded
        Project.objects.create(
            name="Other status",
            repo_url="https://github.com/foo/bar",
            status=Project.STATUS.filesystem_created,
        )
        mock_task.assert_not_called()

        # Should NOT trigger on update
        project.name = "Updated"
        project.save()
        mock_task.assert_not_called()

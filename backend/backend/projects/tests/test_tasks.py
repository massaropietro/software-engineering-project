import pytest
import shutil
import tempfile
import zipfile
from pathlib import Path
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from backend.projects.models import Project

@pytest.fixture
def temp_zip_project(db):
    # Create a dummy zip file
    tmp_dir = tempfile.mkdtemp()
    zip_path = Path(tmp_dir) / "test.zip"

    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr('hello.txt', 'Hello World')
        zf.writestr('subdir/foo.txt', 'Bar')

    with open(zip_path, 'rb') as f:
        file_content = f.read()

    project = Project.objects.create(
        name="Test Zip Project",
        zip_file=SimpleUploadedFile("test.zip", file_content)
    )

    yield project

    shutil.rmtree(tmp_dir)
    if project.zip_file:
        project.zip_file.delete(save=False)

@pytest.mark.django_db
def test_project_signal_triggers_filesystem_build(db):
    with mock.patch("backend.projects.tasks.build_filesystem_task.delay") as mock_task:
        project = Project.objects.create(
            name="Signal Test",
            repo_url="https://example.com"
        )
        # Check that the task was called
        mock_task.assert_called_once_with(project.id)

@pytest.mark.django_db
def test_build_filesystem_task_execution(temp_zip_project):
    # We want to run the actual task synchronously
    from backend.projects.tasks import build_filesystem_task

    # Ensure initial status
    temp_zip_project.status = Project.STATUS.uploaded
    temp_zip_project.save()

    # Run the task directly (bypassing Celery)
    build_filesystem_task(temp_zip_project.id)

    temp_zip_project.refresh_from_db()

    # Check intermediate status was skipped in sync execution, but final status should be correct
    assert temp_zip_project.status == Project.STATUS.filesystem_created
    assert temp_zip_project.file_structure is not None
    assert len(temp_zip_project.file_structure) > 0

import pytest
import zipfile
import tempfile
import shutil
import os
from pathlib import Path
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from backend.projects.models import Project
from backend.projects.services import project_filesystem, update_project_structure

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
def test_project_filesystem_zip(temp_zip_project):
    with project_filesystem(temp_zip_project) as fs_path:
        assert fs_path.exists()
        assert (fs_path / "hello.txt").read_text() == "Hello World"
        assert (fs_path / "subdir" / "foo.txt").read_text() == "Bar"

    # Verify cleanup
    assert not fs_path.exists()

@pytest.mark.django_db
def test_project_filesystem_repo(db):
    project = Project.objects.create(
        name="Test Repo Project",
        repo_url="https://github.com/example/repo.git"
    )

    with mock.patch("subprocess.check_call") as mock_git:
        with project_filesystem(project) as fs_path:
            # We just verify it returns a path and calls git
            # We cannot check if files exist because we mocked git
            assert fs_path.exists()
            mock_git.assert_called_once()
            args = mock_git.call_args[0][0]
            assert args[0] == "git"
            assert args[1] == "clone"
            assert args[4] == project.repo_url
            # The last argument is the path
            assert str(fs_path) == str(args[5])

    # Verify cleanup
    assert not fs_path.exists()

@pytest.mark.django_db
def test_update_project_structure(temp_zip_project):
    update_project_structure(temp_zip_project)

    temp_zip_project.refresh_from_db()
    structure = temp_zip_project.file_structure

    assert structure is not None
    assert len(structure) == 2 # hello.txt and subdir

    # Check for file
    hello_file = next((i for i in structure if i['name'] == 'hello.txt'), None)
    assert hello_file
    assert hello_file['type'] == 'file'
    assert hello_file['path'] == 'hello.txt'

    # Check for directory
    subdir = next((i for i in structure if i['name'] == 'subdir'), None)
    assert subdir
    assert subdir['type'] == 'directory'
    assert subdir['path'] == 'subdir'
    assert 'children' in subdir
    assert len(subdir['children']) > 0
    assert subdir['children'][0]['name'] == 'foo.txt'

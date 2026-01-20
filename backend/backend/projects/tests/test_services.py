import pytest
import zipfile
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from backend.projects.models import Project
from backend.projects.services import (
    project_filesystem,
    update_project_structure,
    build_file_structure_and_save,
)


@pytest.fixture
def temp_zip_project(db):
    # Create a dummy zip file
    tmp_dir = tempfile.mkdtemp()
    zip_path = Path(tmp_dir) / "test.zip"

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("hello.txt", "Hello World")
        zf.writestr("subdir/foo.txt", "Bar")

    with open(zip_path, "rb") as f:
        file_content = f.read()

    project = Project.objects.create(
        name="Test Zip Project", zip_file=SimpleUploadedFile("test.zip", file_content)
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
        name="Test Repo Project", repo_url="https://github.com/example/repo.git"
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
    assert len(structure) == 2  # hello.txt and subdir

    # Check for file
    hello_file = next((i for i in structure if i["name"] == "hello.txt"), None)
    assert hello_file
    assert hello_file["type"] == "file"
    assert hello_file["path"] == "hello.txt"

    # Check for directory
    subdir = next((i for i in structure if i["name"] == "subdir"), None)
    assert subdir
    assert subdir["type"] == "directory"
    assert subdir["path"] == "subdir"
    assert "children" in subdir
    assert len(subdir["children"]) > 0
    assert subdir["children"][0]["name"] == "foo.txt"


@pytest.mark.django_db
def test_project_filesystem_git_failure(db):
    project = Project.objects.create(
        name="Fail Repo Project", repo_url="https://github.com/example/fail.git"
    )

    with mock.patch(
        "subprocess.check_call", side_effect=subprocess.CalledProcessError(1, "git")
    ):
        with pytest.raises(subprocess.CalledProcessError):
            with project_filesystem(project):
                pass


@pytest.mark.django_db
def test_project_filesystem_no_source(db):
    project = Project.objects.create(name="Empty Project")
    # Should yield empty temp dir
    with project_filesystem(project) as fs_path:
        assert fs_path.exists()
        assert fs_path.is_dir()
        # Should be empty
        assert not any(fs_path.iterdir())


@pytest.mark.django_db
def test_build_file_structure_os_error(temp_zip_project):
    with project_filesystem(temp_zip_project) as fs_path:
        with mock.patch("os.scandir", side_effect=OSError("Disk error")):
            structure = build_file_structure_and_save(
                fs_path, temp_zip_project, fs_path
            )
            # Should return empty list and log error (not raise)
            assert structure == []


@pytest.mark.django_db
def test_build_file_structure_file_read_error(temp_zip_project):
    # Create a file that we will simulate read error on
    # We can't easily make a truly unreadable file in temp without changing perms which might be flaky
    # So we simulate validation/processing error by patching ProjectFile.objects.update_or_create
    # OR patching open()

    with project_filesystem(temp_zip_project) as fs_path:
        # Patch open to raise exception
        original_open = open

        def side_effect(file, *args, **kwargs):
            if str(file).endswith("hello.txt"):
                raise Exception("Read failed")
            return original_open(file, *args, **kwargs)

        with mock.patch("builtins.open", side_effect=side_effect):
            structure = build_file_structure_and_save(
                fs_path, temp_zip_project, fs_path
            )

        # Structure should still contain the file, but content not saved?
        # Actually logic is: catch generic Exception inside the loop
        # item is created before the try block for content reading
        # Wait, looking at code:
        # item = {...}
        # if entry.is_dir(): ...
        # else: try: ... except: logger.warning ... items.append(item)
        # So the item is added even if read fails.

        hello_item = next((i for i in structure if i["name"] == "hello.txt"), None)
        assert hello_item is not None
        # file_id might be missing if save failed?
        # The code sets item["file_id"] INSIDE the try block after save.
        # So if save fails, file_id will be missing.
        assert "file_id" not in hello_item

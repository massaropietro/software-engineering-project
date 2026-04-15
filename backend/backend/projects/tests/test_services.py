import pytest
import zipfile
import tempfile
import shutil
import subprocess
import sqlite3
from pathlib import Path
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from backend.projects.models import Project, MutationAnalysis
from backend.projects.services import (
    get_project_source_path,
    update_project_structure,
    get_file_content_from_source,
    run_mutation_analysis,
    _parse_mutmut_results,
)


@pytest.fixture
def temp_zip_project(db):
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
def test_get_project_source_path(db):
    project = Project.objects.create(name="Test Path")
    expected_path = Path(settings.MEDIA_ROOT) / "_projects_sources" / str(project.id) / "source"
    assert get_project_source_path(project) == expected_path


@pytest.mark.django_db
def test_update_project_structure_zip(temp_zip_project):
    update_project_structure(temp_zip_project)

    temp_zip_project.refresh_from_db()
    structure = temp_zip_project.file_structure

    assert structure is not None
    assert len(structure) == 2  # hello.txt and subdir

    hello_file = next((i for i in structure if i["name"] == "hello.txt"), None)
    assert hello_file and hello_file["type"] == "file"

    subdir = next((i for i in structure if i["name"] == "subdir"), None)
    assert subdir and subdir["type"] == "directory"
    assert len(subdir["children"]) == 1
    
    # Check that disk files exist
    source_path = get_project_source_path(temp_zip_project)
    assert (source_path / "hello.txt").exists()
    assert (source_path / "subdir" / "foo.txt").exists()


@pytest.mark.django_db
def test_update_project_structure_repo(db):
    project = Project.objects.create(
        name="Test Repo Project", repo_url="https://github.com/example/repo.git"
    )

    with mock.patch("subprocess.check_call") as mock_git:
        update_project_structure(project)
        mock_git.assert_called_once()
        args = mock_git.call_args[0][0]
        assert args[0] == "git"
        assert args[1] == "clone"
        assert args[4] == project.repo_url


@pytest.mark.django_db
def test_get_file_content_from_source(temp_zip_project):
    update_project_structure(temp_zip_project)
    
    content = get_file_content_from_source(temp_zip_project, "hello.txt")
    assert content == "Hello World"
    
    content = get_file_content_from_source(temp_zip_project, "subdir/foo.txt")
    assert content == "Bar"


@pytest.mark.django_db
def test_get_file_content_invalid_path(temp_zip_project):
    update_project_structure(temp_zip_project)
    
    with pytest.raises(ValueError, match="Invalid file path"):
        get_file_content_from_source(temp_zip_project, "../../../etc/passwd")

    with pytest.raises(FileNotFoundError):
        get_file_content_from_source(temp_zip_project, "nonexistent.txt")


@pytest.mark.django_db
def test_run_mutation_analysis(temp_zip_project):
    update_project_structure(temp_zip_project)
    
    analysis = MutationAnalysis.objects.create(
        project=temp_zip_project,
        files=["hello.txt"],
        status="running"
    )
    
    # Mock subprocess.run
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(stdout="mutmut run", stderr="")
        
        # Mock parsing sqlite results
        with mock.patch("backend.projects.services._parse_mutmut_results") as mock_parse:
            mock_parse.return_value = [
                {"mutant_id": "1", "file": "hello.txt", "line": 1, "status": "killed", "description": ""},
                {"mutant_id": "2", "file": "hello.txt", "line": 2, "status": "survived", "description": ""}
            ]
            
            run_mutation_analysis(analysis)
            
            # Verify setup.cfg was created
            source_path = get_project_source_path(temp_zip_project)
            setup_cfg = source_path / "setup.cfg"
            assert setup_cfg.exists()
            assert "paths_to_mutate = hello.txt" in setup_cfg.read_text()
            assert "pytest_add_cli_args_test_selection = ." in setup_cfg.read_text()

            # Verify command was just "mutmut run" and env was set
            mock_run.assert_called_once()
            _, kwargs = mock_run.call_args
            called_env = kwargs.get("env")
            assert "PYTHONPATH" in called_env
            assert "mutants" in called_env["PYTHONPATH"]
            
            # Verify pytest.ini was created in mutants subdir
            mutants_ini = source_path / "mutants" / "pytest.ini"
            assert mutants_ini.exists()
            content = mutants_ini.read_text()
            assert "addopts" in content
            assert "-p no:cov" in content
            assert "-p no:anyio" in content
            assert "-p no:faker" in content
            assert mock_run.call_args[0][0] == ["mutmut", "run"]
            
            analysis.refresh_from_db()
            assert analysis.score == 50.0
            assert analysis.raw_output == "mutmut run"
            
            assert analysis.mutants.count() == 2
            assert analysis.mutants.filter(status="killed").exists()
            assert analysis.mutants.filter(status="survived").exists()
@pytest.mark.django_db
def test_update_project_structure_no_source(db):
    project = Project.objects.create(name="Empty")
    update_project_structure(project)
    assert project.file_structure == []

@pytest.mark.django_db
def test_update_project_structure_git_fail(db):
    project = Project.objects.create(name="Fail", repo_url="https://invalid.url")
    with mock.patch("subprocess.check_call", side_effect=subprocess.CalledProcessError(1, "git")):
        with pytest.raises(subprocess.CalledProcessError):
            update_project_structure(project)

@pytest.mark.django_db
def test_get_file_content_binary(temp_zip_project):
    update_project_structure(temp_zip_project)
    source_path = get_project_source_path(temp_zip_project)
    binary_file = source_path / "binary.bin"
    binary_file.write_bytes(b"\x80\x81\x82")
    
    content = get_file_content_from_source(temp_zip_project, "binary.bin")
    assert content == "<Binary file or unsupported encoding>"

@pytest.mark.django_db
def test_parse_mutmut_results_missing_cache(db):
    assert _parse_mutmut_results(Path("nonexistent")) == []

@pytest.mark.django_db
def test_parse_mutmut_results_error(db):
    with tempfile.NamedTemporaryFile() as tmp:
        # Invalid sqlite file
        Path(tmp.name).write_text("not a database")
        assert _parse_mutmut_results(Path(tmp.name)) == []
@pytest.mark.django_db
def test_build_file_structure_oserror(db):
    from backend.projects.services import _build_file_structure
    with mock.patch("os.scandir", side_effect=OSError("Access denied")):
        results = _build_file_structure(Path("/tmp"), Path("/tmp"))
        assert results == []

@pytest.mark.django_db
def test_update_project_structure_zip_fallback(temp_zip_project):
    with mock.patch("zipfile.ZipFile.extractall", side_effect=[NotImplementedError, None]):
        # First call fails with NotImplementedError, second (fallback) should succeed
        update_project_structure(temp_zip_project)
        assert temp_zip_project.file_structure is not None

@pytest.mark.django_db
def test_parse_mutmut_results_alternate_schema(db):
    from backend.projects.services import _parse_mutmut_results
    with tempfile.NamedTemporaryFile() as tmp:
        conn = sqlite3.connect(tmp.name)
        # Create a table with MISSING columns to trigger OperationalError
        conn.execute("CREATE TABLE mutant (wrong_col TEXT)")
        conn.commit()
        conn.close()
        
        # Should not crash, should return empty list and log warning
        assert _parse_mutmut_results(Path(tmp.name)) == []

@pytest.mark.django_db
def test_run_mutation_analysis_stderr(temp_zip_project):
    update_project_structure(temp_zip_project)
    analysis = MutationAnalysis.objects.create(project=temp_zip_project, files=[])
    
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(stdout="ok", stderr="some warning")
        with mock.patch("backend.projects.services._parse_mutmut_results") as mock_parse:
            mock_parse.return_value = []
            run_mutation_analysis(analysis)
            assert analysis.raw_output == "oksome warning"

@pytest.mark.django_db
def test_install_deps_reqs(db):
    from backend.projects.services import _install_project_dependencies
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "requirements.txt").write_text("pytest")
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0)
            _install_project_dependencies(p)
            assert mock_run.called
            # Our implementation tries 'uv' first
            assert "uv" in str(mock_run.call_args_list[0][0][0])
            assert "requirements.txt" in str(mock_run.call_args_list[0][0][0])

@pytest.mark.django_db
def test_install_deps_pyproject(db):
    from backend.projects.services import _install_project_dependencies
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        (p / "pyproject.toml").write_text("[project]")
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0)
            _install_project_dependencies(p)
            assert mock_run.called
            # Our implementation tries 'uv' first
            assert "uv" in str(mock_run.call_args_list[0][0][0])
            assert "." in str(mock_run.call_args_list[0][0][0])

@pytest.mark.django_db
def test_run_mutation_analysis_missing_source(db):
    project = Project.objects.create(name="No Source")
    analysis = MutationAnalysis.objects.create(project=project)
    # get_project_source_path(project).exists() is False
    with pytest.raises(FileNotFoundError, match="Source directory for project"):
        run_mutation_analysis(analysis)

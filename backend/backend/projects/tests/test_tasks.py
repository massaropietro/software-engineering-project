import pytest
import shutil
import tempfile
import zipfile
from pathlib import Path
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile
from backend.projects.models import Project, MutationAnalysis


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
def test_project_signal_triggers_filesystem_build(db):
    with mock.patch("backend.projects.tasks.build_filesystem_task.delay") as mock_task:
        project = Project.objects.create(
            name="Signal Test", repo_url="https://example.com"
        )
        mock_task.assert_called_once_with(project.id)


@pytest.mark.django_db
def test_build_filesystem_task_execution(temp_zip_project):
    from backend.projects.tasks import build_filesystem_task

    temp_zip_project.status = Project.STATUS.uploaded
    temp_zip_project.save()

    build_filesystem_task(temp_zip_project.id)

    temp_zip_project.refresh_from_db()

    assert temp_zip_project.status == Project.STATUS.filesystem_created
    assert temp_zip_project.file_structure is not None
    assert len(temp_zip_project.file_structure) > 0


@pytest.mark.django_db
def test_build_filesystem_task_project_not_found(caplog):
    from backend.projects.tasks import build_filesystem_task

    build_filesystem_task(99999)

    assert "Project 99999 not found" in caplog.text


@pytest.mark.django_db
def test_build_filesystem_task_generic_exception(temp_zip_project):
    from backend.projects.tasks import build_filesystem_task

    temp_zip_project.status = Project.STATUS.uploaded
    temp_zip_project.save()

    with mock.patch(
        "backend.projects.tasks.update_project_structure", side_effect=Exception("Boom")
    ):
        build_filesystem_task(temp_zip_project.id)

    temp_zip_project.refresh_from_db()

    assert temp_zip_project.status == Project.STATUS.filesystem_build_failed


@pytest.mark.django_db
def test_run_mutation_analysis_task(temp_zip_project):
    from backend.projects.tasks import run_mutation_analysis_task
    
    analysis = MutationAnalysis.objects.create(project=temp_zip_project)
    
    with mock.patch("backend.projects.tasks.run_mutation_analysis") as mock_run:
        run_mutation_analysis_task(analysis.id)
        
        analysis.refresh_from_db()
        assert analysis.status == MutationAnalysis.STATUS.completed
        mock_run.assert_called_once_with(analysis)


@pytest.mark.django_db
def test_run_mutation_analysis_task_exception(temp_zip_project):
    from backend.projects.tasks import run_mutation_analysis_task
    
    analysis = MutationAnalysis.objects.create(project=temp_zip_project)
    
    with mock.patch("backend.projects.tasks.run_mutation_analysis", side_effect=Exception("Boom")):
        run_mutation_analysis_task(analysis.id)
        
        analysis.refresh_from_db()
        assert analysis.status == MutationAnalysis.STATUS.failed
@pytest.mark.django_db
def test_run_mutation_analysis_task_not_found(caplog):
    from backend.projects.tasks import run_mutation_analysis_task
    run_mutation_analysis_task("00000000-0000-0000-0000-000000000000")
    assert "MutationAnalysis 00000000-0000-0000-0000-000000000000 not found" in caplog.text

@pytest.mark.django_db
def test_build_filesystem_task_critical_error_project_gone(db):
    from backend.projects.tasks import build_filesystem_task
    project = Project.objects.create(name="Temp")
    
    with mock.patch("backend.projects.tasks.update_project_structure", side_effect=Exception("Boom")):
        with mock.patch("backend.projects.tasks.logger.exception") as mock_log:
            with mock.patch("backend.projects.models.Project.objects.get", side_effect=[project, Project.DoesNotExist]):
                # First get succeeds, second (in error handler) fails
                build_filesystem_task(project.id)
                
    assert mock_log.called
    assert "Error building filesystem" in mock_log.call_args[0][0]

@pytest.mark.django_db
def test_run_mutation_analysis_task_critical_error_analysis_gone(db):
    from backend.projects.tasks import run_mutation_analysis_task
    project = Project.objects.create(name="Temp")
    analysis = MutationAnalysis.objects.create(project=project)
    
    with mock.patch("backend.projects.tasks.run_mutation_analysis", side_effect=Exception("Boom")):
        with mock.patch("backend.projects.tasks.logger.exception") as mock_log:
            with mock.patch("backend.projects.models.MutationAnalysis.objects.get", side_effect=MutationAnalysis.DoesNotExist):
                # We use select_related("project").get(...) in the task, 
                # but simply patching the manager's get often works if not select_related'ed
                # In tasks.py: MutationAnalysis.objects.select_related("project").get(id=analysis_id)
                with mock.patch("backend.projects.models.MutationAnalysis.objects.select_related") as mock_select:
                    mock_select.return_value.get.side_effect = [analysis, MutationAnalysis.DoesNotExist]
                    run_mutation_analysis_task(analysis.id)
    
    assert mock_log.called
    assert "Error running mutation analysis" in mock_log.call_args[0][0]
@pytest.mark.django_db
def test_run_mutation_analysis_task_auto_build(temp_zip_project):
    from backend.projects.tasks import run_mutation_analysis_task
    
    # Set project status to uploaded (not yet filesystem_created)
    temp_zip_project.status = Project.STATUS.uploaded
    temp_zip_project.save()
    
    analysis = MutationAnalysis.objects.create(project=temp_zip_project)
    
    with mock.patch("backend.projects.tasks.update_project_structure") as mock_build:
        with mock.patch("backend.projects.tasks.run_mutation_analysis") as mock_run:
            run_mutation_analysis_task(analysis.id)
            
            # Verify build was called
            mock_build.assert_called_once_with(temp_zip_project)
            # Verify run was called
            mock_run.assert_called_once_with(analysis)
            
            temp_zip_project.refresh_from_db()
            assert temp_zip_project.status == Project.STATUS.filesystem_created
            
            analysis.refresh_from_db()
            assert analysis.status == MutationAnalysis.STATUS.completed

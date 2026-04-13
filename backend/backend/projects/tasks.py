import logging

from celery import shared_task

from backend.projects.models import MutationAnalysis, Project
from backend.projects.services import run_mutation_analysis, update_project_structure

logger = logging.getLogger(__name__)


@shared_task
def build_filesystem_task(project_id):
    """
    Clones/extracts the project into the persistent media storage directory
    and updates the file_structure JSON field.
    """
    try:
        project = Project.objects.get(id=project_id)

        project.status = Project.STATUS.building_filesystem
        project.save()

        logger.info(f"Building filesystem for project {project_id}")

        update_project_structure(project)

        project.status = Project.STATUS.filesystem_created
        project.save()

        logger.info(f"Filesystem built for project {project_id}")

    except Project.DoesNotExist:
        logger.error(f"Project {project_id} not found")
    except Exception as e:
        logger.exception(f"Error building filesystem for project {project_id}: {e}")
        try:
            project = Project.objects.get(id=project_id)
            project.status = Project.STATUS.filesystem_build_failed
            project.save()
        except Project.DoesNotExist:
            pass


@shared_task(soft_time_limit=3600, time_limit=3900)
def run_mutation_analysis_task(analysis_id):
    """
    Runs mutmut on the project source and stores results in MutationResult rows.
    """
    try:
        analysis = MutationAnalysis.objects.select_related("project").get(id=analysis_id)

        analysis.status = MutationAnalysis.STATUS.running
        analysis.save()

        # Ensure filesystem is ready, if not, try to build it now
        if analysis.project.status != Project.STATUS.filesystem_created:
            logger.info(f"Project filesystem not ready for analysis {analysis_id}. Attempting build.")
            update_project_structure(analysis.project)
            analysis.project.status = Project.STATUS.filesystem_created
            analysis.project.save()

        logger.info(f"Running mutation analysis {analysis_id}")

        run_mutation_analysis(analysis)

        analysis.status = MutationAnalysis.STATUS.completed
        analysis.save()

        logger.info(f"Mutation analysis {analysis_id} completed")

    except MutationAnalysis.DoesNotExist:
        logger.error(f"MutationAnalysis {analysis_id} not found")
    except Exception as e:
        logger.exception(f"Error running mutation analysis {analysis_id}: {e}")
        try:
            analysis = MutationAnalysis.objects.get(id=analysis_id)
            analysis.status = MutationAnalysis.STATUS.failed
            analysis.save()
        except MutationAnalysis.DoesNotExist:
            pass

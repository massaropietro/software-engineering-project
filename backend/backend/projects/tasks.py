from celery import shared_task
from backend.projects.models import Project
from backend.projects.services import update_project_structure
import logging

logger = logging.getLogger(__name__)

@shared_task
def build_filesystem_task(project_id):
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
            project.status = Project.STATUS.failed
            project.save()
        except:
            pass

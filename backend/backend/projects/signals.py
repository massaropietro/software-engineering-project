import shutil
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from pathlib import Path

from backend.projects.models import Project
from backend.projects.tasks import build_filesystem_task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Project)
def trigger_filesystem_build(sender, instance, created, **kwargs):
    if created and instance.status == Project.STATUS.uploaded:
        build_filesystem_task.delay(instance.id)


@receiver(post_delete, sender=Project)
def delete_project_filesystem(sender, instance, **kwargs):
    try:
        project_dir = Path(settings.MEDIA_ROOT) / "_projects_sources" / str(instance.id)
        if project_dir.exists():
            shutil.rmtree(project_dir)
            logger.info(f"Successfully deleted project directory for project {instance.id}")

        if instance.zip_file:
            instance.zip_file.delete(save=False)
            logger.info(f"Successfully deleted zip file for project {instance.id}")
    except Exception as e:
        logger.error(f"Error deleting filesystem for project {instance.id}: {e}")

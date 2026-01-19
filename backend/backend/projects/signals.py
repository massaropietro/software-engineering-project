from django.db.models.signals import post_save
from django.dispatch import receiver
from backend.projects.models import Project
from backend.projects.tasks import build_filesystem_task

@receiver(post_save, sender=Project)
def trigger_filesystem_build(sender, instance, created, **kwargs):
    if created and instance.status == Project.STATUS.uploaded:
        build_filesystem_task.delay(instance.id)

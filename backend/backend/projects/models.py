from django.db import models

from model_utils.models import StatusModel
from model_utils.choices import Choices

from django.utils.translation import gettext_lazy as _

from backend.core.models import BaseModel
from .validators import ProjectValidator


class Project(BaseModel, StatusModel):
    Validator = ProjectValidator

    STATUS = Choices(
        "uploaded", "processing_classes", "analysing", "failed", "completed"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    zip_file = models.FileField(upload_to="projects/zips/", blank=True, null=True)
    repo_url = models.URLField(blank=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        return f"{self.name} ({self.status})"

from django.db import models

from model_utils.models import StatusModel
from model_utils.choices import Choices

from django.utils.translation import gettext_lazy as _

from backend.core.models import BaseModel
from .validators import ProjectValidator


class Project(BaseModel, StatusModel):
    Validator = ProjectValidator

    STATUS = Choices(
        "uploaded",
        "building_filesystem",
        "filesystem_created",
        "processing_classes",
        "analysing",
        "failed",
        "completed",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    zip_file = models.FileField(upload_to="projects/zips/", blank=True, null=True)
    repo_url = models.URLField(blank=True)
    file_structure = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        return f"{self.name} ({self.status})"


class ProjectFile(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="files")
    path = models.CharField(max_length=1024, db_index=True)
    content = models.TextField(blank=True, null=True)
    size = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("Project File")
        verbose_name_plural = _("Project Files")
        unique_together = ("project", "path")
        ordering = ["path"]

    def __str__(self):
        return f"{self.project.name} - {self.path}"

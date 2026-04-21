import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.choices import Choices
from model_utils.models import StatusModel

from backend.core.models import BaseModel
from .validators import ProjectValidator


class Project(BaseModel, StatusModel):
    Validator = ProjectValidator

    STATUS = Choices(
        "uploaded",
        "building_filesystem",
        "filesystem_created",
        "filesystem_build_failed",
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

    # Genera automaticamente un UUID univoco e non modificabile alla creazione
    secret_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        return f"{self.name} ({self.status})"


class MutationAnalysis(BaseModel, StatusModel):
    STATUS = Choices(
        "pending",
        "running",
        "completed",
        "failed",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="mutation_analyses",
    )
    files = models.JSONField(
        default=list,
        blank=True,
        help_text=_("List of file/directory paths relative to project root to mutate"),
    )
    language = models.CharField(max_length=50, default="python")
    score = models.FloatField(blank=True, null=True)
    raw_output = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Mutation Analysis")
        verbose_name_plural = _("Mutation Analyses")
        ordering = ["-created"]

    def __str__(self):
        return f"Analysis({self.project.name}, {self.status})"


class MutationResult(BaseModel):
    RESULT_STATUS = Choices(
        ("killed", _("Killed")),
        ("survived", _("Survived")),
        ("timeout", _("Timeout")),
        ("suspicious", _("Suspicious")),
    )

    analysis = models.ForeignKey(
        MutationAnalysis,
        on_delete=models.CASCADE,
        related_name="mutants",
    )
    file = models.CharField(max_length=1024)
    mutant_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=RESULT_STATUS)
    is_equivalent = models.BooleanField(
        null=True,
        blank=True,
        help_text=_("True if Z3 + LLM classified this mutant as equivalent."),
    )
    line = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Mutation Result")
        verbose_name_plural = _("Mutation Results")
        ordering = ["file", "mutant_id"]

    def __str__(self):
        return f"Mutant #{self.mutant_id} [{self.status}] in {self.file}"

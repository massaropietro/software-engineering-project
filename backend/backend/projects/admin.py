from django.contrib import admin

from .models import MutationAnalysis, MutationResult, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created")
    list_filter = ("status",)
    search_fields = ("name",)


@admin.register(MutationAnalysis)
class MutationAnalysisAdmin(admin.ModelAdmin):
    list_display = ("project", "language", "status", "score", "created")
    list_filter = ("status", "language")
    search_fields = ("project__name",)
    raw_id_fields = ("project",)


@admin.register(MutationResult)
class MutationResultAdmin(admin.ModelAdmin):
    list_display = ("analysis", "file", "mutant_id", "status", "line")
    list_filter = ("status",)
    search_fields = ("file", "mutant_id")
    raw_id_fields = ("analysis",)

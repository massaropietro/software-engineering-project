from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.projects"

    def ready(self):
        try:
            import backend.projects.signals  # noqa: F401
        except ImportError:
            pass

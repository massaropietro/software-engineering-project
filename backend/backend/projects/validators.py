from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ProjectValidator:
    def validate(self, project):
        if not project.zip_file and not project.repo_url:
            raise ValidationError(
                _("You must provide either a zip file or a repository URL.")
            )

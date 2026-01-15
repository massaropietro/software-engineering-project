from django.db import models

from model_utils.models import UUIDModel, TimeStampedModel

class BaseModel(UUIDModel, TimeStampedModel):
    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        validator_class = getattr(self, "Validator", None)
        if validator_class:
            validator_class().validate(self)

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.serializers import as_serializer_error


def drf_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = DRFValidationError(as_serializer_error(exc))

    response = exception_handler(exc, context)

    return response

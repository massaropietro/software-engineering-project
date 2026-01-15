from backend.projects.api.serializers import ProjectSerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

def run_verification():
    print("--- START API VERIFICATION ---")

    # Case 1: Invalid Data (No zip/url)
    data = {"name": "API Test 1"}
    serializer = ProjectSerializer(data=data)

    try:
        # We expect this to raise DjangoValidationError because validate() calls clean()
        # and ProjectSerializer doesn't catch it (the View exception handler handles it).
        serializer.is_valid(raise_exception=True)
        print("Case 1 Failed: Validation succeeded unexpectedly.")
    except DjangoValidationError as e:
        print(f"Case 1 Success: Caught expected DjangoValidationError: {e}")
    except DRFValidationError as e:
        print(f"Case 1 Warning: Caught DRFValidationError: {e}. (Did you catch it in serializer?)")
    except Exception as e:
        print(f"Case 1 Failed: Unexpected exception: {type(e).__name__}: {e}")

    print("--- END API VERIFICATION ---")

if __name__ == "__main__":
    run_verification()

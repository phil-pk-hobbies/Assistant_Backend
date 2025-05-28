from django.core.exceptions import ValidationError
from django.db import transaction


def assert_fileid_unique_across_models(file_id: str, lock: bool = False) -> None:
    """Raise ValidationError if ``file_id`` exists in AssistantFile or ThreadFile."""
    from assistants.models import AssistantFile  # imported here to avoid circulars
    from chat.models import ThreadFile

    qs_a = AssistantFile.objects
    qs_t = ThreadFile.objects
    if lock:
        qs_a = qs_a.select_for_update()
        qs_t = qs_t.select_for_update()
    if qs_a.filter(file_id=file_id).exists() or qs_t.filter(file_id=file_id).exists():
        raise ValidationError("duplicate_in_other_scope")

"""Normalize extended catalog metadata before persistence."""

from copy import deepcopy
from datetime import datetime
from decimal import Decimal, InvalidOperation


COMMON_FIELDS = """
site_keys publication_ready content_version updated_at price currency
""".split()

COURSE_FIELDS = """
record_type marketing_slug target_audience prerequisite_course_keys
recommended_prerequisites level delivery_format language assessment_summary
completion_requirements takeaway credential enrollment_url waitlist_url
syllabus_url parent_course sequence_in_course standards_alignment
""".split()

PROGRAM_FIELDS = """
duration_minutes_min duration_minutes_max microcourse_price ksa weeks
elective_groups target_audience roles_prepared_for entry_requirements
work_products capstone examination exam_blueprint certificate_term
award_title standards_alignment sample_work_url enrollment_url waitlist_url
""".split()

ARRAY_FIELDS = set("""
site_keys prerequisite_course_keys recommended_prerequisites
standards_alignment weeks elective_groups roles_prepared_for
work_products exam_blueprint
""".split())

OBJECT_FIELDS = {"ksa", "capstone", "examination"}


def decimal_price(value):
    """Return an exact approved price, or None for a pending price."""
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("A price cannot be a boolean.")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("Price must be a decimal or null.") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError("Price must be finite and nonnegative.")
    if amount > Decimal("99999999.99"):
        raise ValueError("Price exceeds the supported maximum.")
    rounded = amount.quantize(Decimal("0.01"))
    if rounded != amount:
        raise ValueError("Price cannot contain fractional cents.")
    return rounded


def extended_metadata_defaults(record, kind, sidecar=None):
    """Map supplied fields; retain source data outside public serializers."""
    if not isinstance(record, dict):
        raise ValueError("Catalog record must be an object.")
    if kind not in {"microcourse", "program"}:
        raise ValueError("Unknown catalog record kind.")
    if sidecar is not None and not isinstance(sidecar, dict):
        raise ValueError("Sidecar must be an object.")

    fields = COMMON_FIELDS + (
        COURSE_FIELDS if kind == "microcourse" else PROGRAM_FIELDS
    )
    values = {
        name: deepcopy(record[name])
        for name in fields
        if name in record
    }

    # Missing approval must never retain an earlier true approval implicitly.
    values.setdefault("publication_ready", False)
    if not isinstance(values["publication_ready"], bool):
        raise ValueError("publication_ready must be a boolean.")

    for name in ARRAY_FIELDS & values.keys():
        if not isinstance(values[name], list):
            raise ValueError(f"{name} must be an array.")
    for name in OBJECT_FIELDS & values.keys():
        if not isinstance(values[name], dict):
            raise ValueError(f"{name} must be an object.")

    for name in ("price", "microcourse_price"):
        if name in values:
            values[name] = decimal_price(values[name])

    if "currency" in values:
        currency = values["currency"]
        if not isinstance(currency, str):
            raise ValueError("currency must be a string.")
        currency = currency.strip().upper()
        if len(currency) != 3 or not currency.isascii() or not currency.isalpha():
            raise ValueError("currency must be a three-letter code.")
        values["currency"] = currency

    if values.get("updated_at") is not None:
        raw = values["updated_at"]
        if not isinstance(raw, str):
            raise ValueError("updated_at must be an ISO timestamp or null.")
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("updated_at is not a valid ISO timestamp.") from exc
        if parsed.utcoffset() is None:
            raise ValueError("updated_at must include its timezone.")
        values["updated_at"] = parsed

    if kind == "microcourse" and sidecar is not None:
        for name in ("parent_course", "sequence_in_course"):
            if name not in values and name in sidecar:
                values[name] = deepcopy(sidecar[name])

    for name in (
        "sequence_in_course", "duration_minutes_min", "duration_minutes_max"
    ):
        value = values.get(name)
        if value is not None and (
            type(value) is not int or value < 1
        ):
            raise ValueError(f"{name} must be a positive integer or null.")

    lower = values.get("duration_minutes_min")
    upper = values.get("duration_minutes_max")
    if lower is not None and upper is not None and lower > upper:
        raise ValueError("Maximum duration cannot be below minimum duration.")

    authoring = deepcopy(record.get("authoring_metadata", {}))
    if not isinstance(authoring, dict):
        raise ValueError("authoring_metadata must be an object.")

    authoring["source_record"] = deepcopy({
        name: value
        for name, value in record.items()
        if name != "authoring_metadata"
    })
    if sidecar is not None:
        authoring["sidecar"] = deepcopy(sidecar)

    values["authoring_metadata"] = authoring
    return values

"""Validate staff-supplied approved Studio exports before catalog synchronization."""

from datetime import datetime

from .credit_contract import normalize_credit_plan


def approved_course_export(payload):
    if not isinstance(payload, dict) or payload.get("schema_version") != "cba-credit-plan-v1":
        raise ValueError("Supply a credit-plan export from Studio.")
    key = payload.get("course_key")
    if not isinstance(key, str) or not key.startswith("course-v1:"):
        raise ValueError("The export must identify its course run.")
    raw = payload.get("credit_plan")
    if not isinstance(raw, dict) or raw.get("status") != "approved":
        raise ValueError("Only approved Studio plans can be synchronized.")
    approval = payload.get("approval")
    if not isinstance(approval, dict) or type(approval.get("approved_by_id")) is not int:
        raise ValueError("The export must include its approval audit record.")
    if approval["approved_by_id"] <= 0:
        raise ValueError("An approval actor is required.")
    try:
        stamp = datetime.fromisoformat(approval["approved_at"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("An approval timestamp is required.") from exc
    if stamp.utcoffset() is None:
        raise ValueError("The approval timestamp must include its timezone.")
    return key, normalize_credit_plan(raw, "microcourse", draft_only=False), approval

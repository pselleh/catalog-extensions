"""Catalog-only planned credits. This module never creates learner awards."""

from copy import deepcopy

from .credit_calculations import ACTIVITY_CATEGORIES, CREDIT_POLICY_VERSION, calculate_credits


def normalize_credit_plan(raw, kind, *, draft_only=True):
    if not isinstance(raw, dict):
        raise ValueError("credit_plan must be an object.")
    if not raw:
        return {}
    if kind not in {"microcourse", "program"}:
        raise ValueError("Unknown credit-plan record kind.")
    version = raw.get("version", 1)
    if type(version) is not int or not 1 <= version <= 2147483647:
        raise ValueError("credit_plan.version must be a positive integer.")
    basis = "program_total" if kind == "program" else "course_total"
    if kind == "program" and raw.get("basis") != basis:
        raise ValueError("Program credit plans must explicitly use basis='program_total', including all course and program work once.")
    if raw.get("basis", basis) != basis:
        raise ValueError("Incorrect credit-plan calculation basis.")
    if raw.get("policy_version", CREDIT_POLICY_VERSION) != CREDIT_POLICY_VERSION:
        raise ValueError("Unsupported credit policy version.")
    minutes = deepcopy(raw.get("activity_minutes", {name: None for name in ACTIVITY_CATEGORIES}))
    calculate_credits(minutes)
    status = raw.get("status", "draft")
    if status not in {"draft", "approved"}:
        raise ValueError("credit_plan.status must be draft or approved.")
    if status == "approved" and not draft_only:
        totals = calculate_credits(minutes)
        if totals.eligible_minutes is None or totals.eligible_minutes <= 0:
            raise ValueError("Approved planned credits require complete, positive eligible time.")
    # Ignore supplied credit totals; compute from eligible minutes every time.
    result = {
        "version": version, "status": "draft" if draft_only else status,
        "basis": basis, "activity_minutes": minutes,
        "policy_version": CREDIT_POLICY_VERSION,
    }
    for name in ("instructional_design_reference", "learning_outcomes", "required_block_keys", "activity_requirements"):
        if name in raw:
            result[name] = deepcopy(raw[name])
    return result


def credit_summary(raw, kind, *, include_draft=False):
    empty = {
        "status": "pending", "version": None,
        "basis": "program_total" if kind == "program" else "course_total",
        "policy_version": CREDIT_POLICY_VERSION,
        "activity_minutes": {name: None for name in ACTIVITY_CATEGORIES},
        "eligible_minutes": None, "pdu": None, "ceu": None,
    }
    try:
        plan = normalize_credit_plan(raw, kind, draft_only=False)
        if not plan:
            return empty
        result = {**empty, **{name: plan[name] for name in ("status", "version", "basis", "policy_version")}}
        if plan["status"] != "approved" and not include_draft:
            return result
        totals = calculate_credits(plan["activity_minutes"])
        result.update(
            activity_minutes=plan["activity_minutes"], eligible_minutes=totals.eligible_minutes,
            pdu=str(totals.pdu) if totals.pdu is not None else None,
            ceu=str(totals.ceu) if totals.ceu is not None else None,
        )
        return result
    except (ValueError, TypeError):
        return {**empty, "status": "invalid"}


def approved_program_budget(raw, member_plans, *, has_electives=False):
    """Validate a whole-program budget without adding component credits twice."""
    if has_electives:
        raise ValueError("Programs with electives need an explicit approved pathway before a single credit total can be approved.")
    if not isinstance(raw, dict):
        raise ValueError("A program credit plan is required.")
    plan = normalize_credit_plan({**raw, "status": "approved"}, "program", draft_only=False)
    if not isinstance(plan.get("instructional_design_reference"), str) or not plan["instructional_design_reference"].strip():
        raise ValueError("Program approval requires an instructional design reference.")
    outcomes = plan.get("learning_outcomes")
    if not isinstance(outcomes, list) or not outcomes or any(not isinstance(item, str) or not item.strip() for item in outcomes):
        raise ValueError("Program approval requires intended learning outcomes.")
    if not member_plans:
        raise ValueError("Required program microcourses must be defined before approval.")
    minimums = {name: 0 for name in ACTIVITY_CATEGORIES}
    for raw_member in member_plans:
        member = normalize_credit_plan(raw_member, "microcourse", draft_only=False)
        if not member or member["status"] != "approved":
            raise ValueError("Each required microcourse needs an approved credit plan.")
        for name in ACTIVITY_CATEGORIES:
            minimums[name] += member["activity_minutes"][name]
    if any(plan["activity_minutes"][name] < minimums[name] for name in ACTIVITY_CATEGORIES):
        raise ValueError("The whole-program budget cannot omit required microcourse activity time.")
    return plan

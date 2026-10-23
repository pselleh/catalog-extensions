from copy import deepcopy
from unittest import TestCase

from catalog_extensions.services.credit_contract import credit_summary, normalize_credit_plan, approved_program_budget
from catalog_extensions.services.catalog_payload import extended_metadata_defaults


class CatalogCreditContractTests(TestCase):
    def plan(self, **changes):
        result = {
            "version": 1, "status": "approved",
            "activity_minutes": {"instruction": 60, "assignments": 15, "assessments": 10, "discussions": 5, "other": 0},
        }
        result.update(changes)
        return result

    def test_bulk_import_always_produces_draft_credits(self):
        result = extended_metadata_defaults({"credit_plan": self.plan()}, "microcourse")
        self.assertEqual(result["credit_plan"]["status"], "draft")

    def test_sidecar_credit_plan_uses_the_same_mapping(self):
        result = extended_metadata_defaults({}, "microcourse", {"credit_plan": self.plan()})
        self.assertEqual(result["credit_plan"]["activity_minutes"]["instruction"], 60)
        self.assertEqual(result["credit_plan"]["status"], "draft")

    def test_conflicting_sidecar_credit_plan_is_rejected(self):
        with self.assertRaises(ValueError):
            extended_metadata_defaults({"credit_plan": self.plan()}, "microcourse", {"credit_plan": self.plan(version=2)})

    def test_missing_credit_plan_is_pending(self):
        self.assertIsNone(credit_summary({}, "microcourse")["pdu"])
        self.assertEqual(credit_summary({}, "microcourse")["status"], "pending")

    def test_approved_totals_include_all_eligible_work(self):
        result = credit_summary(self.plan(), "microcourse")
        self.assertEqual(result["eligible_minutes"], 90)
        self.assertEqual(result["pdu"], "1.5000")
        self.assertEqual(result["ceu"], "0.1500")

    def test_public_summary_does_not_advertise_unapproved_totals(self):
        result = credit_summary(self.plan(status="draft"), "microcourse")
        self.assertEqual(result["status"], "draft")
        self.assertIsNone(result["pdu"])

    def test_draft_preview_can_be_computed_privately(self):
        result = credit_summary(self.plan(status="draft"), "microcourse", include_draft=True)
        self.assertEqual(result["pdu"], "1.5000")

    def test_credits_are_not_taken_from_supplied_totals(self):
        result = credit_summary(self.plan(pdu="999", ceu="999"), "microcourse")
        self.assertEqual(result["pdu"], "1.5000")

    def test_program_requires_explicit_whole_program_basis(self):
        with self.assertRaises(ValueError):
            normalize_credit_plan(self.plan(), "program")
        result = credit_summary(self.plan(basis="program_total"), "program")
        self.assertEqual(result["eligible_minutes"], 90)

    def test_program_total_is_not_added_to_member_course_totals(self):
        result = credit_summary(self.plan(basis="program_total", member_pdu="999"), "program")
        self.assertEqual(result["pdu"], "1.5000")

    def test_invalid_time_cannot_be_advertised(self):
        raw = self.plan()
        raw["activity_minutes"]["instruction"] = True
        self.assertEqual(credit_summary(raw, "microcourse")["status"], "invalid")

    def test_unknown_time_is_not_approved(self):
        raw = self.plan()
        raw["activity_minutes"]["instruction"] = None
        self.assertEqual(credit_summary(raw, "microcourse")["status"], "invalid")

    def test_public_response_excludes_private_design_and_passing_rules(self):
        result = credit_summary(self.plan(
            instructional_design_reference="private", required_block_keys=["private"],
            activity_requirements=[{"private": "rule"}],
        ), "microcourse")
        self.assertNotIn("required_block_keys", result)
        self.assertNotIn("activity_requirements", result)
        self.assertNotIn("instructional_design_reference", result)

    def test_normalization_does_not_change_source(self):
        raw = self.plan()
        before = deepcopy(raw)
        normalized = normalize_credit_plan(raw, "microcourse")
        normalized["activity_minutes"]["instruction"] = 1
        self.assertEqual(raw, before)

    def program_plan(self):
        return self.plan(basis="program_total", status="draft", instructional_design_reference="IDP-PROGRAM", learning_outcomes=["Assess risk."])

    def test_program_approval_does_not_double_add_member_time(self):
        plan = approved_program_budget(self.program_plan(), [self.plan()])
        self.assertEqual(credit_summary(plan, "program")["pdu"], "1.5000")

    def test_program_cannot_omit_required_member_time(self):
        raw = self.program_plan()
        raw["activity_minutes"]["instruction"] = 30
        with self.assertRaises(ValueError):
            approved_program_budget(raw, [self.plan()])

    def test_program_cannot_use_draft_member_credits(self):
        with self.assertRaises(ValueError):
            approved_program_budget(self.program_plan(), [self.plan(status="draft")])

    def test_program_electives_require_a_defined_path(self):
        with self.assertRaises(ValueError):
            approved_program_budget(self.program_plan(), [self.plan()], has_electives=True)

    def test_program_without_required_courses_is_not_approved(self):
        with self.assertRaises(ValueError):
            approved_program_budget(self.program_plan(), [])

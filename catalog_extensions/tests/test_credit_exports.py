from unittest import TestCase

from catalog_extensions.services.credit_exports import approved_course_export


class ApprovedCreditExportTests(TestCase):
    def payload(self):
        return {
            "schema_version": "cba-credit-plan-v1", "course_key": "course-v1:ERPI+TEST+2027",
            "approval": {"approved_by_id": 1, "approved_at": "2026-10-23T12:00:00+00:00"},
            "credit_plan": {"version": 1, "status": "approved", "activity_minutes": {
                "instruction": 60, "assignments": 0, "assessments": 0, "discussions": 0, "other": 0,
            }},
        }

    def test_approved_export_keeps_course_identity_and_audit(self):
        key, plan, audit = approved_course_export(self.payload())
        self.assertEqual(key, "course-v1:ERPI+TEST+2027")
        self.assertEqual(plan["status"], "approved")
        self.assertEqual(audit["approved_by_id"], 1)

    def test_draft_export_is_rejected(self):
        payload = self.payload()
        payload["credit_plan"]["status"] = "draft"
        with self.assertRaises(ValueError):
            approved_course_export(payload)

    def test_missing_approval_is_rejected(self):
        payload = self.payload()
        payload.pop("approval")
        with self.assertRaises(ValueError):
            approved_course_export(payload)

    def test_naive_timestamp_is_rejected(self):
        payload = self.payload()
        payload["approval"]["approved_at"] = "2026-10-23T12:00:00"
        with self.assertRaises(ValueError):
            approved_course_export(payload)

    def test_unknown_eligible_time_is_rejected(self):
        payload = self.payload()
        payload["credit_plan"]["activity_minutes"]["instruction"] = None
        with self.assertRaises(ValueError):
            approved_course_export(payload)

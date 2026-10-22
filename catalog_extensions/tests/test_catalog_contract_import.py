from decimal import Decimal
from unittest.mock import patch

from django.core.management.base import CommandError
from django.test import SimpleTestCase

from catalog_extensions.management.commands.import_cba_catalog import Command


class CatalogContractImportTests(SimpleTestCase):
    def setUp(self):
        self.command = Command()

    def test_course_fields_and_sidecar_are_preserved(self):
        sidecar = {
            "parent_course": "REG01",
            "sequence_in_course": 2,
            "ai_brief": {"performance_outcome": "Assess risk"},
        }
        self.command.catalog_sidecars = {"course-v1:CBA+TEST+2026": sidecar}
        record = {
            "course_key": "course-v1:CBA+TEST+2026",
            "price": None,
            "target_audience": "Risk practitioners",
            "publication_ready": False,
        }

        values = self.command._extended_metadata_defaults(record)

        self.assertIsNone(values["price"])
        self.assertEqual(values["target_audience"], "Risk practitioners")
        self.assertEqual(values["parent_course"], "REG01")
        self.assertEqual(values["sequence_in_course"], 2)
        self.assertEqual(values["authoring_metadata"]["source_record"], record)
        self.assertEqual(values["authoring_metadata"]["sidecar"], sidecar)

        values["authoring_metadata"]["sidecar"]["ai_brief"].clear()
        self.assertEqual(
            sidecar["ai_brief"]["performance_outcome"], "Assess risk"
        )

    def test_program_fields_and_decimal_price_are_mapped(self):
        values = self.command._extended_metadata_defaults({
            "program_code": "RPC",
            "price": "590.00",
            "microcourse_price": None,
            "duration_minutes_min": 120,
            "duration_minutes_max": 180,
            "ksa": {"knowledge": ["Risk assessment"]},
            "award_title": "Practice Certificate",
        })

        self.assertEqual(values["price"], Decimal("590.00"))
        self.assertIsNone(values["microcourse_price"])
        self.assertEqual(values["duration_minutes_min"], 120)
        self.assertEqual(values["duration_minutes_max"], 180)
        self.assertEqual(values["ksa"]["knowledge"], ["Risk assessment"])
        self.assertEqual(values["award_title"], "Practice Certificate")

    def test_invalid_prices_raise_command_errors(self):
        for price in (True, "-1", "NaN", "Infinity", "59.001"):
            with self.subTest(price=price):
                with self.assertRaises(CommandError):
                    self.command._extended_metadata_defaults({"price": price})

    def test_invalid_duration_range_raises_command_error(self):
        with self.assertRaises(CommandError):
            self.command._extended_metadata_defaults({
                "program_code": "RPC",
                "duration_minutes_min": 180,
                "duration_minutes_max": 120,
            })

    def test_null_price_does_not_touch_seats_or_currency(self):
        module = "catalog_extensions.management.commands.import_cba_catalog"
        with patch(module + ".Currency") as currency, patch(
            module + ".SeatType"
        ) as seat_type, patch(module + ".Seat") as seat:
            self.command._upsert_seat(object(), None, "USD")

        currency.objects.get.assert_not_called()
        seat_type.objects.get_or_create.assert_not_called()
        seat.objects.update_or_create.assert_not_called()

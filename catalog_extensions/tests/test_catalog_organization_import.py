import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.management.base import CommandError
from django.test import SimpleTestCase

from catalog_extensions.management.commands.import_cba_catalog import Command


MODULE = "catalog_extensions.management.commands.import_cba_catalog"


class CatalogOrganizationImportTests(SimpleTestCase):
    def setUp(self):
        self.command = Command()
        self.command.defer_images = True
        example = (
            Path(__file__).resolve().parents[2]
            / "docs/api/cba_catalog_import.example.json"
        )
        self.record = json.loads(example.read_text())["microcourses"][0]
        self.record["owning_organization"] = "ERPI"
        self.record["listing_organizations"] = ["ERPI", "PB"]
        self.partner = SimpleNamespace(pk=10)

    def test_course_import_saves_owner_and_listing_relationships(self):
        owner = SimpleNamespace(key="ERPI")
        listings = [owner, SimpleNamespace(key="PB")]
        saved = MagicMock()
        with patch(MODULE + ".CourseRun") as runs, patch(
            MODULE + ".MicrocourseCatalogMetadata"
        ) as metadata, patch(
            MODULE + ".resolve_organizations",
            return_value=(owner, listings),
        ) as resolver:
            run = runs.objects.select_related.return_value.get.return_value
            run.course.partner_id = self.partner.pk
            metadata.objects.update_or_create.return_value = (saved, False)
            self.command._upsert_seat = MagicMock()
            self.command._replace_course_faculty = MagicMock()

            self.command._import_microcourses(
                [self.record], {},
                {key: MagicMock() for key in self.record["catalog_categories"]},
                partner=self.partner,
            )

            resolver.assert_called_once_with(self.record, self.partner)
            self.assertIs(saved.owning_organization, owner)
            saved.save.assert_called_once_with(
                update_fields=["owning_organization"]
            )
            saved.listing_organizations.set.assert_called_once_with(listings)
            run.course.authoring_organizations.set.assert_not_called()

    def test_course_from_other_partner_is_rejected_before_writing(self):
        with patch(MODULE + ".CourseRun") as runs, patch(
            MODULE + ".resolve_organizations"
        ) as resolver:
            run = runs.objects.select_related.return_value.get.return_value
            run.course.partner_id = 99
            with self.assertRaisesMessage(CommandError, "different Discovery partner"):
                self.command._import_microcourses(
                    [self.record], {}, {}, partner=self.partner
                )
            run.course.save.assert_not_called()
            resolver.assert_not_called()

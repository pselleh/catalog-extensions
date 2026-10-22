from types import SimpleNamespace
from unittest.mock import patch

from django.core.management.base import CommandError
from django.test import SimpleTestCase

from catalog_extensions.services.catalog_organizations import (
    organization_keys,
    resolve_organizations,
)


class CatalogOrganizationTests(SimpleTestCase):
    def test_existing_organization_is_default_owner_and_listing(self):
        self.assertEqual(
            organization_keys({"organization": "CBA"}),
            ("CBA", ["CBA"]),
        )

    def test_catalog_owner_does_not_change_studio_organization(self):
        record = {
            "organization": "CBA",
            "owning_organization": "ERPI",
            "listing_organizations": ["ERPI", "PB"],
        }
        self.assertEqual(
            organization_keys(record), ("ERPI", ["ERPI", "PB"])
        )
        self.assertEqual(record["organization"], "CBA")

    def test_explicit_empty_listings_are_preserved(self):
        self.assertEqual(
            organization_keys({
                "owning_organization": "ERPI",
                "listing_organizations": [],
            }),
            ("ERPI", []),
        )

    def test_invalid_organization_values_are_rejected(self):
        cases = [
            {"owning_organization": None},
            {"owning_organization": " "},
            {"listing_organizations": "ERPI"},
            {"listing_organizations": [None]},
            {"listing_organizations": ["ERPI", " ERPI "]},
        ]
        for record in cases:
            with self.subTest(record=record):
                with self.assertRaises(ValueError):
                    organization_keys(record)

    def test_resolution_is_scoped_to_selected_partner(self):
        partner = object()
        owner = SimpleNamespace(key="ERPI")
        other = SimpleNamespace(key="PB")
        module = "catalog_extensions.services.catalog_organizations"
        with patch(module + ".Organization") as model:
            model.objects.filter.return_value = [owner, other]
            actual = resolve_organizations({
                "owning_organization": "ERPI",
                "listing_organizations": ["PB", "ERPI"],
            }, partner)
            model.objects.filter.assert_called_once_with(
                partner=partner, key__in={"ERPI", "PB"}
            )
        self.assertEqual(actual, (owner, [other, owner]))

    def test_missing_organization_stops_resolution(self):
        module = "catalog_extensions.services.catalog_organizations"
        with patch(module + ".Organization") as model:
            model.objects.filter.return_value = []
            with self.assertRaisesMessage(CommandError, "ERPI"):
                resolve_organizations({
                    "owning_organization": "ERPI",
                }, object())

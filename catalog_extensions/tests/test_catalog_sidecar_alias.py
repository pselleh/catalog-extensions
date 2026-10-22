from django.test import SimpleTestCase

from catalog_extensions.management.commands.import_cba_catalog import Command


class CatalogSidecarAliasTests(SimpleTestCase):
    def setUp(self):
        self.command = Command()
        self.command.defer_images = True
        self.key = "course-v1:CBA+TEST+2027"
        self.sidecar = {
            "parent_course": "REG01",
            "sequence_in_course": 2,
            "ai_brief": {"performance_outcome": "Assess risk"},
        }

    def test_singular_source_sidecar_reaches_metadata(self):
        self.assertEqual(
            self.command._validate({"sidecar": {self.key: self.sidecar}}),
            [],
        )
        values = self.command._extended_metadata_defaults({
            "course_key": self.key,
        })
        self.assertEqual(
            values["authoring_metadata"]["sidecar"], self.sidecar
        )
        self.assertEqual(values["parent_course"], "REG01")

    def test_plural_sidecars_remain_supported(self):
        self.assertEqual(
            self.command._validate({"sidecars": {self.key: self.sidecar}}),
            [],
        )
        self.assertEqual(
            self.command.catalog_sidecars, {self.key: self.sidecar}
        )

    def test_conflicting_aliases_are_rejected(self):
        errors = self.command._validate({
            "sidecar": {self.key: self.sidecar},
            "sidecars": {},
        })
        self.assertTrue(any("must match" in error for error in errors))

    def test_invalid_sidecar_shapes_are_rejected(self):
        for name in ("sidecar", "sidecars"):
            for value in (None, [], {self.key: "invalid"}):
                with self.subTest(name=name, value=value):
                    self.assertTrue(
                        self.command._validate({name: value})
                    )

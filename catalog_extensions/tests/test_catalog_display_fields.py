from types import SimpleNamespace

from django.test import SimpleTestCase

from catalog_extensions.api.serializers.catalog_display import (
    COMMON_DISPLAY_FIELDS,
    COURSE_DISPLAY_FIELDS,
    PROGRAM_DISPLAY_FIELDS,
    CourseDisplayMetadataSerializer,
    ProgramDisplayMetadataSerializer,
)
from catalog_extensions.api.serializers.course import (
    CourseListSerializer,
    CourseRunSerializer,
)
from catalog_extensions.api.serializers.program import ProgramSerializer
from catalog_extensions.tests.test_catalog_serializers import (
    RelatedCollection,
    category,
    course,
    course_metadata,
    course_run,
    program,
    program_metadata,
)


class CatalogDisplayFieldTests(SimpleTestCase):
    def test_course_responses_include_display_fields_and_null_price(self):
        primary = category("organizational-resilience")
        metadata = course_metadata(primary, primary)
        metadata.owning_organization = SimpleNamespace(key="ERPI")
        metadata.listing_organizations = RelatedCollection(
            SimpleNamespace(key="ERPI")
        )
        metadata.target_audience = "Risk practitioners"
        metadata.record_type = "microcourse"
        metadata.publication_ready = True
        metadata.price = None
        metadata.currency = "USD"
        metadata.authoring_metadata = {"private_note": "Do not publish"}
        run = course_run(metadata)

        for serializer in (
            CourseRunSerializer(run),
            CourseListSerializer(course(run)),
        ):
            with self.subTest(serializer=type(serializer).__name__):
                data = serializer.data
                self.assertEqual(data["owning_organization"], "ERPI")
                self.assertEqual(data["listing_organizations"], ["ERPI"])
                self.assertEqual(data["target_audience"], "Risk practitioners")
                self.assertEqual(data["record_type"], "microcourse")
                self.assertIsNone(data["price"])
                self.assertEqual(data["currency"], "USD")
                self.assertNotIn("authoring_metadata", data)

    def test_program_response_includes_extended_fields_and_null_price(self):
        primary = category("organizational-resilience")
        metadata = program_metadata(primary, primary)
        metadata.price = None
        metadata.microcourse_price = None
        metadata.award_title = "Practice Certificate"
        metadata.duration_minutes_min = 120
        metadata.duration_minutes_max = 180
        metadata.ksa = {"knowledge": ["Risk assessment"]}
        metadata.authoring_metadata = {"private_note": "Do not publish"}

        data = ProgramSerializer(program(metadata)).data

        self.assertIsNone(data["price"])
        self.assertIsNone(data["microcourse_price"])
        self.assertEqual(data["award_title"], "Practice Certificate")
        self.assertEqual(data["duration_minutes_min"], 120)
        self.assertEqual(data["duration_minutes_max"], 180)
        self.assertEqual(data["ksa"], {"knowledge": ["Risk assessment"]})
        self.assertNotIn("authoring_metadata", data)

    def test_display_serializers_use_explicit_field_lists(self):
        self.assertEqual(
            set(CourseDisplayMetadataSerializer().fields),
            set(COMMON_DISPLAY_FIELDS + COURSE_DISPLAY_FIELDS),
        )
        self.assertEqual(
            set(ProgramDisplayMetadataSerializer().fields),
            set(COMMON_DISPLAY_FIELDS + PROGRAM_DISPLAY_FIELDS),
        )
        for serializer in (
            CourseDisplayMetadataSerializer(),
            ProgramDisplayMetadataSerializer(),
        ):
            self.assertNotIn("authoring_metadata", serializer.fields)
            self.assertTrue(all(
                field.read_only for field in serializer.fields.values()
            ))

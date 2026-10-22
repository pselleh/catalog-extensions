from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from catalog_extensions.api.serializers.course import CourseListSerializer
from catalog_extensions.api.views.programs import (
    ProgramDetailView,
    _matches_listing,
)
from catalog_extensions.tests.test_catalog_serializers import (
    category,
    course,
    course_metadata,
    course_run,
    program,
    program_metadata,
)


class CatalogPublicationReadyTests(SimpleTestCase):
    def test_public_courses_require_explicit_readiness(self):
        primary = category("organizational-resilience")
        for readiness in (False, None):
            with self.subTest(readiness=readiness):
                metadata = course_metadata(primary, primary)
                if readiness is None:
                    del metadata.publication_ready
                else:
                    metadata.publication_ready = readiness
                obj = course(course_run(metadata))
                self.assertEqual(
                    CourseListSerializer()._runs(obj), []
                )

    def test_internal_courses_can_include_unapproved_records(self):
        primary = category("organizational-resilience")
        metadata = course_metadata(primary, primary)
        metadata.publication_ready = False
        run = course_run(metadata)
        obj = course(run)
        serializer = CourseListSerializer(context={"public_only": False})
        self.assertEqual(serializer._runs(obj), [run])

    def test_public_program_detail_rejects_unapproved_record(self):
        primary = category("organizational-resilience")
        metadata = program_metadata(primary, primary)
        metadata.publication_ready = False
        obj = program(metadata)
        request = SimpleNamespace(query_params={})
        with patch(
            "catalog_extensions.api.views.programs.ProgramService"
        ) as service:
            service.return_value.get_program.return_value = obj
            response = ProgramDetailView().get(request, uuid=obj.uuid)
        self.assertEqual(response.status_code, 404)

    def test_internal_program_listing_check_accepts_unapproved_record(self):
        primary = category("organizational-resilience")
        metadata = program_metadata(primary, primary)
        metadata.publication_ready = False
        obj = program(metadata)
        request = SimpleNamespace(query_params={})
        self.assertTrue(
            _matches_listing(obj, request, public_only=False)
        )

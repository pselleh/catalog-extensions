from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from catalog_extensions.api.serializers.program import ProgramSerializer
from catalog_extensions.api.views.programs import ProgramDetailView
from catalog_extensions.tests.test_catalog_serializers import (
    RelatedCollection,
    category,
    course,
    course_metadata,
    course_run,
    program,
    program_metadata,
)


class ProgramListingResponseTests(SimpleTestCase):
    def member(self, suffix, organization, visibility="public"):
        primary = category("organizational-resilience")
        metadata = course_metadata(primary, primary)
        metadata.catalog_visibility = visibility
        metadata.listing_organizations = RelatedCollection(
            SimpleNamespace(key=organization)
        )
        run = course_run(metadata)
        run.key = f"course-v1:CBA+TEST+{suffix}"
        obj = course(run)
        run.course = obj
        return obj, SimpleNamespace(
            course_run=run, sequence=int(suffix), required=True
        )

    def test_public_program_members_are_filtered_without_program_status_filter(self):
        primary = category("organizational-resilience")
        obj = program(program_metadata(primary, primary))
        matching, requirement = self.member("1", "ERPI")
        other, other_requirement = self.member("2", "PB")
        hidden, hidden_requirement = self.member("3", "ERPI", "hidden")
        obj.courses = RelatedCollection(matching, other, hidden)
        obj.cba_course_requirements = RelatedCollection(
            requirement, other_requirement, hidden_requirement
        )
        serializer = ProgramSerializer(context={
            "request": SimpleNamespace(query_params={
                "orgcode": "ERPI",
                "catalog_status": "planned",
            }),
            "public_only": True,
        })

        courses = serializer.get_courses(obj)
        requirements = serializer.get_microcourses(obj)
        self.assertEqual(
            [item["course_key"] for item in courses],
            [requirement.course_run.key],
        )
        self.assertEqual(
            [item["microcourse"]["course_key"] for item in requirements],
            [requirement.course_run.key],
        )

    def test_internal_program_members_can_include_hidden_runs(self):
        primary = category("organizational-resilience")
        obj = program(program_metadata(primary, primary))
        hidden, requirement = self.member("1", "ERPI", "hidden")
        obj.courses = RelatedCollection(hidden)
        obj.cba_course_requirements = RelatedCollection(requirement)
        serializer = ProgramSerializer(context={
            "request": SimpleNamespace(query_params={"orgcode": "ERPI"}),
            "public_only": False,
        })

        self.assertEqual(len(serializer.get_courses(obj)), 1)
        self.assertEqual(len(serializer.get_microcourses(obj)), 1)

    def test_program_detail_rejects_other_listing_organization(self):
        primary = category("organizational-resilience")
        metadata = program_metadata(primary, primary)
        metadata.listing_organizations = RelatedCollection(
            SimpleNamespace(key="PB")
        )
        obj = program(metadata)
        request = SimpleNamespace(query_params={"orgcode": "ERPI"})
        with patch(
            "catalog_extensions.api.views.programs.ProgramService"
        ) as service:
            service.return_value.get_program.return_value = obj
            response = ProgramDetailView().get(request, uuid=obj.uuid)

        self.assertEqual(response.status_code, 404)

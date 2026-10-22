from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from catalog_extensions.api.serializers.course import CourseListSerializer
from catalog_extensions.api.views.programs import ProgramDetailView
from catalog_extensions.repositories.course_repository import CourseRepository
from catalog_extensions.repositories.program_repository import ProgramRepository
from catalog_extensions.tests.test_catalog_serializers import (
    RelatedCollection,
    category,
    course,
    course_metadata,
    course_run,
    program,
    program_metadata,
)


class CatalogSiteFilterTests(SimpleTestCase):
    def queryset(self):
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        queryset.distinct.return_value = queryset
        return queryset

    def test_course_site_and_organization_share_run_filter(self):
        repository = CourseRepository()
        queryset = self.queryset()
        with patch.object(repository, "_base_queryset", return_value=queryset):
            repository.list_courses(filters={
                "organization": "ERPI", "site": "site-a",
            })
        queryset.filter.assert_called_once_with(
            course_runs__cba_catalog__site_keys__contains=["site-a"],
            course_runs__cba_catalog__listing_organizations__key="ERPI",
            course_runs__cba_catalog__catalog_visibility="public",
        )

    def test_program_query_filters_site_membership(self):
        repository = ProgramRepository()
        queryset = self.queryset()
        with patch.object(repository, "_base_queryset", return_value=queryset):
            repository.list_programs(filters={"site": "site-a"})
        queryset.filter.assert_any_call(
            cba_catalog__site_keys__contains=["site-a"]
        )

    def test_course_serializer_selects_run_for_requested_site(self):
        primary = category("organizational-resilience")
        first_metadata = course_metadata(primary, primary)
        first_metadata.site_keys = ["site-a"]
        second_metadata = course_metadata(primary, primary)
        second_metadata.site_keys = ["site-b"]
        first = course_run(first_metadata)
        second = course_run(second_metadata)
        first.key = "course-v1:CBA+TEST+2026"
        second.key = "course-v1:CBA+TEST+2027"
        obj = course(first)
        obj.course_runs = RelatedCollection(first, second)

        serializer = CourseListSerializer(context={
            "request": SimpleNamespace(query_params={"site": "site-b"}),
        })
        self.assertIs(serializer._run(obj), second)
        self.assertEqual(serializer._runs(obj), [second])

    def test_program_detail_rejects_wrong_site(self):
        primary = category("organizational-resilience")
        metadata = program_metadata(primary, primary)
        metadata.site_keys = ["site-a"]
        obj = program(metadata)
        request = SimpleNamespace(query_params={"site": "site-b"})
        with patch(
            "catalog_extensions.api.views.programs.ProgramService"
        ) as service:
            service.return_value.get_program.return_value = obj
            response = ProgramDetailView().get(request, uuid=obj.uuid)
        self.assertEqual(response.status_code, 404)

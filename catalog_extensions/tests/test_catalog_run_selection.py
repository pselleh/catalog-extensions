from types import SimpleNamespace

from django.test import SimpleTestCase

from catalog_extensions.api.serializers.course import (
    CourseDetailSerializer,
    CourseListSerializer,
)
from catalog_extensions.tests.test_catalog_serializers import (
    RelatedCollection,
    category,
    course,
    course_metadata,
    course_run,
)


class CatalogRunSelectionTests(SimpleTestCase):
    def run_for(self, key, organization, visibility="public"):
        primary = category("organizational-resilience")
        metadata = course_metadata(primary, primary)
        metadata.listing_organizations = RelatedCollection(
            SimpleNamespace(key=organization)
        )
        metadata.catalog_visibility = visibility
        run = course_run(metadata)
        run.key = key
        return run

    def context(self, **params):
        return {"request": SimpleNamespace(query_params=params)}

    def test_matching_run_replaces_unrelated_advertised_run(self):
        advertised = self.run_for("course-v1:CBA+TEST+2026", "PB")
        matching = self.run_for("course-v1:CBA+TEST+2027", "ERPI")
        obj = course(advertised)
        obj.course_runs = RelatedCollection(advertised, matching)

        data = CourseListSerializer(
            obj, context=self.context(orgcode="ERPI")
        ).data
        self.assertEqual(data["course_key"], matching.key)

    def test_detail_nested_runs_exclude_other_orgs_and_hidden_runs(self):
        matching = self.run_for("course-v1:CBA+TEST+2027", "ERPI")
        other = self.run_for("course-v1:CBA+TEST+2026", "PB")
        hidden = self.run_for("course-v1:CBA+TEST+2028", "ERPI", "hidden")
        obj = course(matching)
        obj.course_runs = RelatedCollection(other, matching, hidden)
        serializer = CourseDetailSerializer(
            context=self.context(orgcode="ERPI")
        )

        data = serializer.get_course_runs(obj)
        self.assertEqual([item["course_key"] for item in data], [matching.key])

    def test_exact_run_key_controls_selection(self):
        advertised = self.run_for("course-v1:CBA+TEST+2026", "ERPI")
        requested = self.run_for("course-v1:CBA+TEST+2027", "ERPI")
        obj = course(advertised)
        obj.course_runs = RelatedCollection(advertised, requested)
        context = self.context(orgcode="ERPI")
        context["course_key"] = requested.key
        serializer = CourseDetailSerializer(context=context)

        self.assertIs(serializer._run(obj), requested)
        self.assertEqual(serializer._runs(obj), [requested])

    def test_internal_context_can_select_hidden_run(self):
        hidden = self.run_for("course-v1:CBA+TEST+2027", "ERPI", "hidden")
        obj = course(hidden)
        context = self.context(orgcode="ERPI")
        self.assertEqual(CourseListSerializer(context=context)._runs(obj), [])

        context["public_only"] = False
        self.assertEqual(
            CourseListSerializer(context=context)._runs(obj), [hidden]
        )

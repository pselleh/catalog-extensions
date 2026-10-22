from django.contrib.sites.models import Site
from django.test import TestCase

from course_discovery.apps.core.models import Partner
from course_discovery.apps.course_metadata.models import (
    Course, CourseRun, Organization, Program, ProgramType,
)

from catalog_extensions.api.serializers.catalog_display import (
    CourseDisplayMetadataSerializer,
)
from catalog_extensions.models.course import MicrocourseCatalogMetadata
from catalog_extensions.models.program import CertificateProgramCatalogMetadata
from catalog_extensions.repositories.course_repository import CourseRepository
from catalog_extensions.repositories.program_repository import ProgramRepository
from catalog_extensions.services.catalog_organizations import resolve_organizations


class CatalogDatabaseTests(TestCase):
    def insert_native(self, obj, **lookup):
        # Fixture creation bypasses native save hooks and search indexing.
        type(obj).objects.bulk_create([obj])
        return type(obj).objects.get(**lookup)

    def setUp(self):
        site = self.insert_native(
            Site(domain="catalog-test.invalid", name="Catalog test"),
            domain="catalog-test.invalid",
        )
        self.partner = self.insert_native(
            Partner(name="Catalog test", short_code="ct", site=site),
            short_code="ct",
        )
        self.owner = self.insert_native(
            Organization(partner=self.partner, key="ERPI", name="ERPI test"),
            partner=self.partner, key="ERPI",
        )
        self.course = self.insert_native(
            Course(partner=self.partner, key="CBA+CATALOGTEST", title="Test course"),
            partner=self.partner, key="CBA+CATALOGTEST",
        )
        self.run = self.insert_native(
            CourseRun(
                course=self.course,
                key="course-v1:CBA+CATALOGTEST+2027",
                pacing_type="self_paced",
            ),
            course=self.course, key="course-v1:CBA+CATALOGTEST+2027",
        )
        self.metadata = MicrocourseCatalogMetadata.objects.create(
            course_run=self.run,
            owning_organization=self.owner,
            site_keys=["site-a"],
            publication_ready=True,
            catalog_visibility="public",
            catalog_status="waitlist_open",
            price=None,
            authoring_metadata={"sidecar": {"internal_note": "Preserved"}},
        )
        self.metadata.listing_organizations.set([self.owner])

        program_type = ProgramType.objects.get(slug="certificate")
        self.program = self.insert_native(
            Program(
                partner=self.partner,
                type=program_type,
                title="Test certificate",
                marketing_slug="catalog-database-test",
            ),
            partner=self.partner, marketing_slug="catalog-database-test",
        )
        self.program_metadata = CertificateProgramCatalogMetadata.objects.create(
            program=self.program,
            program_code="CATALOG-DB-TEST",
            owning_organization=self.owner,
            site_keys=["site-a"],
            publication_ready=True,
            catalog_visibility="public",
            catalog_status="waitlist_open",
            price=None,
        )
        self.program_metadata.listing_organizations.set([self.owner])

    def test_metadata_relationships_and_null_price_round_trip(self):
        self.metadata.refresh_from_db()
        self.assertEqual(self.metadata.owning_organization, self.owner)
        self.assertEqual(
            list(self.metadata.listing_organizations.values_list("key", flat=True)),
            ["ERPI"],
        )
        self.assertIsNone(self.metadata.price)
        self.assertEqual(
            self.metadata.authoring_metadata["sidecar"]["internal_note"],
            "Preserved",
        )
        data = CourseDisplayMetadataSerializer(self.metadata).data
        self.assertEqual(data["owning_organization"], "ERPI")
        self.assertEqual(data["listing_organizations"], ["ERPI"])
        self.assertIsNone(data["price"])
        self.assertNotIn("authoring_metadata", data)

    def test_course_query_matches_site_org_and_readiness_on_same_run(self):
        repository = CourseRepository()
        filters = {"organization": "ERPI", "site": "site-a"}
        self.assertTrue(repository.list_courses(filters=filters).exists())
        self.assertFalse(repository.list_courses(filters={
            "organization": "ERPI", "site": "site-b",
        }).exists())

        other = self.insert_native(
            CourseRun(
                course=self.course,
                key="course-v1:CBA+CATALOGTEST+2028",
                pacing_type="self_paced",
            ),
            course=self.course, key="course-v1:CBA+CATALOGTEST+2028",
        )
        other_metadata = MicrocourseCatalogMetadata.objects.create(
            course_run=other,
            site_keys=["site-b"],
            publication_ready=True,
            catalog_visibility="public",
        )
        other_metadata.listing_organizations.set([self.owner])
        self.metadata.publication_ready = False
        self.metadata.save(update_fields=["publication_ready"])

        self.assertFalse(repository.list_courses(filters=filters).exists())
        self.assertTrue(repository.list_courses(
            filters=filters, public_only=False,
        ).exists())

    def test_program_query_matches_site_org_and_readiness(self):
        repository = ProgramRepository()
        filters = {"organization": "ERPI", "site": "site-a"}
        self.assertTrue(repository.list_programs(filters=filters).exists())
        self.assertFalse(repository.list_programs(filters={
            "organization": "ERPI", "site": "site-b",
        }).exists())

        self.program_metadata.publication_ready = False
        self.program_metadata.save(update_fields=["publication_ready"])
        self.assertFalse(repository.list_programs(filters=filters).exists())
        self.assertTrue(repository.list_programs(
            filters=filters, public_only=False,
        ).exists())

    def test_organization_resolver_uses_database_relationships(self):
        owner, listings = resolve_organizations({
            "organization": "CBA",
            "owning_organization": "ERPI",
            "listing_organizations": ["ERPI"],
        }, self.partner)
        self.assertEqual(owner, self.owner)
        self.assertEqual(listings, [self.owner])

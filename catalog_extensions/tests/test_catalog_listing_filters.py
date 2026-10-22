from unittest.mock import MagicMock, call, patch
from django.test import SimpleTestCase
from catalog_extensions.repositories.course_repository import CourseRepository
from catalog_extensions.repositories.program_repository import ProgramRepository

class CatalogListingFilterTests(SimpleTestCase):

    def queryset(self):
        queryset = MagicMock()
        queryset.filter.return_value = queryset
        queryset.distinct.return_value = queryset
        return queryset

    def test_course_listing_and_public_conditions_share_one_filter(self):
        repository = CourseRepository()
        queryset = self.queryset()
        with patch.object(repository, '_base_queryset', return_value=queryset):
            repository.list_courses(filters={'organization': 'ERPI', 'catalog_status': 'waitlist_open', 'catalog_category': 'organizational-resilience'})
        queryset.filter.assert_called_once_with(course_runs__cba_catalog__listing_organizations__key='ERPI', course_runs__cba_catalog__catalog_visibility='public', course_runs__cba_catalog__catalog_status='waitlist_open', course_runs__cba_catalog__catalog_categories__key='organizational-resilience', course_runs__cba_catalog__catalog_categories__is_active=True, course_runs__cba_catalog__publication_ready=True)

    def test_internal_course_listing_filter_uses_listing_relationship(self):
        repository = CourseRepository()
        queryset = self.queryset()
        with patch.object(repository, '_base_queryset', return_value=queryset):
            repository.list_courses(filters={'organization': 'PB'}, public_only=False)
        queryset.filter.assert_called_once_with(course_runs__cba_catalog__listing_organizations__key='PB')

    def test_program_listing_filter_uses_listing_relationship(self):
        repository = ProgramRepository()
        queryset = self.queryset()
        with patch.object(repository, '_base_queryset', return_value=queryset):
            repository.list_programs(filters={'organization': 'ERPI'}, public_only=True)
        self.assertEqual(queryset.filter.call_args_list, [call(cba_catalog__catalog_visibility='public', cba_catalog__publication_ready=True), call(cba_catalog__listing_organizations__key='ERPI')])

    def test_default_queries_are_not_sliced_before_pagination(self):
        for repository in (CourseRepository(), ProgramRepository()):
            with self.subTest(repository=type(repository).__name__):
                queryset = self.queryset()
                with patch.object(repository, '_base_queryset', return_value=queryset):
                    if isinstance(repository, CourseRepository):
                        result = repository.list_courses()
                    else:
                        result = repository.list_programs()
                self.assertIs(result, queryset)
                queryset.__getitem__.assert_not_called()

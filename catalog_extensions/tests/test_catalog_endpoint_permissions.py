from types import SimpleNamespace
from unittest.mock import ANY, patch

from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from catalog_extensions.api.views.courses import (
    CourseListView,
    InternalCourseDetailView,
    InternalCourseListView,
)
from catalog_extensions.api.views.programs import (
    InternalProgramDetailView,
    InternalProgramListView,
)


class CatalogEndpointPermissionTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def internal_views(self):
        return (
            (InternalCourseListView, {}),
            (InternalCourseDetailView, {
                "course_key": "course-v1:CBA+TEST+2027",
            }),
            (InternalProgramListView, {}),
            (InternalProgramDetailView, {
                "uuid": "11111111-1111-1111-1111-111111111111",
            }),
        )

    def user(self, permitted=False):
        return SimpleNamespace(
            is_authenticated=True,
            is_superuser=False,
            has_perm=lambda permission: (
                permitted
                and permission == "catalog_extensions.view_restricted_catalog"
            ),
        )

    def test_anonymous_requests_cannot_access_internal_views(self):
        for view, kwargs in self.internal_views():
            with self.subTest(view=view.__name__):
                request = self.factory.get("/")
                response = view.as_view(authentication_classes=[], throttle_classes=[])(
                    request, **kwargs
                )
                self.assertEqual(response.status_code, 403)

    def test_ordinary_users_cannot_access_internal_views(self):
        for view, kwargs in self.internal_views():
            with self.subTest(view=view.__name__):
                request = self.factory.get("/")
                force_authenticate(request, user=self.user())
                response = view.as_view(authentication_classes=[], throttle_classes=[])(
                    request, **kwargs
                )
                self.assertEqual(response.status_code, 403)

    def test_permitted_service_user_can_request_internal_lists(self):
        cases = (
            (
                InternalCourseListView,
                "catalog_extensions.api.views.courses.CourseService",
                "list_courses",
            ),
            (
                InternalProgramListView,
                "catalog_extensions.api.views.programs.ProgramService",
                "list_programs",
            ),
        )
        for view, target, method in cases:
            with self.subTest(view=view.__name__):
                request = self.factory.get("/", {"orgcode": "ERPI"})
                force_authenticate(request, user=self.user(permitted=True))
                with patch(target) as service:
                    operation = getattr(service.return_value, method)
                    operation.return_value = []
                    response = view.as_view(authentication_classes=[], throttle_classes=[])(request)
                    operation.assert_called_once_with(
                        filters=ANY, public_only=False
                    )
                    self.assertEqual(response.status_code, 200)

    def test_conflicting_organization_parameters_return_bad_request(self):
        request = self.factory.get("/", {
            "orgcode": "ERPI",
            "organization": "PB",
        })
        with patch(
            "catalog_extensions.api.views.courses.CourseService"
        ) as service:
            response = CourseListView.as_view(
                authentication_classes=[], throttle_classes=[]
            )(request)
            self.assertEqual(response.status_code, 400)
            service.assert_not_called()

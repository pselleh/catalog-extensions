from django.urls import path

from .views import (
    CourseListView,
    CourseDetailView,
    ProgramListView,
    ProgramDetailView,
    TranscriptView,
)

app_name = "catalog_extensions"

urlpatterns = [
    path("api/catalog/courses/", CourseListView.as_view(), name="catalog-courses"),
    path("api/catalog/courses/<str:course_key>/", CourseDetailView.as_view(), name="catalog-course-detail"),
    path("api/catalog/programs/", ProgramListView.as_view(), name="catalog-programs"),
    path("api/catalog/programs/<uuid:uuid>/", ProgramDetailView.as_view(), name="catalog-program-detail"),
    path("api/records/me/transcript/", TranscriptView.as_view(), name="my-transcript"),
]

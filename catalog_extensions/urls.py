from django.urls import include, path

urlpatterns = [
    path("api/cba/v1/courses/", include("catalog_extensions.urls.courses")),
    path("api/cba/v1/programs/", include("catalog_extensions.urls.programs")),
    path("api/cba/v1/organizations/", include("catalog_extensions.urls.organizations")),
    path("api/cba/v1/subjects/", include("catalog_extensions.urls.subjects")),
    path("api/cba/v1/search/", include("catalog_extensions.urls.search")),
    path("api/cba/v1/media/", include("catalog_extensions.urls.media")),
    path("api/cba/v1/homepage/", include("catalog_extensions.urls.homepage")),
]

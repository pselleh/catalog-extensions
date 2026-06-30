from django.urls import path

from catalog_extensions.api.views.courses import UnifiedCatalogView

urlpatterns = [
    path("", UnifiedCatalogView.as_view(), name="courses"),
]

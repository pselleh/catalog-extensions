from django.apps import AppConfig


class CatalogExtensionsConfig(AppConfig):
    name = "catalog_extensions"

    def ready(self):
        from django.urls import include, path
        import course_discovery.urls

        # Prevent duplicate injection on reload
        if not any("catalog_extensions.urls" in str(p) for p in course_discovery.urls.urlpatterns):
            course_discovery.urls.urlpatterns += [
                path("", include("catalog_extensions.urls")),
            ]

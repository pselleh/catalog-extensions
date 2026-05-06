from django.apps import AppConfig


class CbaCatalogExtensionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cba_catalog_extensions"

    def ready(self):
        from django.conf import settings
        from django.urls import include, path
        import importlib

        root_urlconf = importlib.import_module(settings.ROOT_URLCONF)

        route = path(
            "api/catalog/",
            include("cba_catalog_extensions.urls"),
        )

        existing = [str(p.pattern) for p in root_urlconf.urlpatterns]
        if "api/catalog/" not in existing:
            root_urlconf.urlpatterns.append(route)

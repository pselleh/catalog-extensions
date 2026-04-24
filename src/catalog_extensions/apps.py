from django.apps import AppConfig


class CatalogExtensionsConfig(AppConfig):
    name = "catalog_extensions"

    def ready(self):
        import catalog_extensions.signals  # noqa

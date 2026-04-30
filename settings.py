SECRET_KEY = "dev"

INSTALLED_APPS = [
    "catalog_extensions",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

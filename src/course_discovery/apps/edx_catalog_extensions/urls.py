from django.urls import include, path

app_name = "extensions"

urlpatterns = [
    path("", include("catalog_extensions.urls")),
]

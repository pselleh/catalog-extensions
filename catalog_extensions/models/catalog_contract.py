from django.db import models


class CatalogContractMetadata(models.Model):
    """Shared catalog ownership, release and authoring metadata."""

    owning_organization = models.ForeignKey(
        "course_metadata.Organization",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_owned",
    )
    listing_organizations = models.ManyToManyField(
        "course_metadata.Organization",
        blank=True,
        related_name="%(app_label)s_%(class)s_listed",
    )
    site_keys = models.JSONField(default=list, blank=True)
    publication_ready = models.BooleanField(default=False)
    content_version = models.CharField(max_length=128, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    authoring_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True

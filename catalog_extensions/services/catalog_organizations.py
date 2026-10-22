"""Resolve catalog organizations within one Discovery partner."""

from django.core.management.base import CommandError
from course_discovery.apps.course_metadata.models import Organization


def organization_keys(record):
    """Return owner and listing keys without changing the Studio organization."""
    owner = record.get(
        "owning_organization", record.get("organization", "CBA")
    )
    if not isinstance(owner, str) or not owner.strip():
        raise ValueError("owning_organization must be a nonempty string.")
    owner = owner.strip()

    listings = record.get("listing_organizations", [owner])
    if not isinstance(listings, list):
        raise ValueError("listing_organizations must be an array.")

    normalized = []
    for key in listings:
        if not isinstance(key, str) or not key.strip():
            raise ValueError(
                "listing_organizations must contain nonempty strings."
            )
        normalized.append(key.strip())

    if len(normalized) != len(set(normalized)):
        raise ValueError("listing_organizations must not contain duplicates.")

    return owner, normalized


def resolve_organizations(record, partner):
    """Require existing organizations belonging to the selected partner."""
    try:
        owner_key, listing_keys = organization_keys(record)
    except ValueError as exc:
        raise CommandError(str(exc)) from exc

    requested = {owner_key, *listing_keys}
    organizations = {
        organization.key: organization
        for organization in Organization.objects.filter(
            partner=partner,
            key__in=requested,
        )
    }
    missing = sorted(requested - organizations.keys())
    if missing:
        raise CommandError(
            "Catalog organizations do not exist for the selected partner: "
            + ", ".join(missing)
        )

    return (
        organizations[owner_key],
        [organizations[key] for key in listing_keys],
    )

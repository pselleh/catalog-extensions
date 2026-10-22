from rest_framework.exceptions import ValidationError


def get_catalog_organization(request):
    """Accept provider orgcode while preserving the organization parameter."""
    organization = (request.query_params.get("organization") or "").strip()
    orgcode = (request.query_params.get("orgcode") or "").strip()

    if organization and orgcode and organization != orgcode:
        raise ValidationError({
            "orgcode": "orgcode and organization must match when both are supplied."
        })

    return orgcode or organization or None

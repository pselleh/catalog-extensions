import hashlib
import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog_extensions.models.course import MicrocourseCatalogMetadata
from catalog_extensions.services.credit_exports import approved_course_export


class Command(BaseCommand):
    help = "Synchronize an approved, trusted Studio credit export to Discovery. Does not publish catalog listings."

    def add_arguments(self, parser):
        parser.add_argument("export_file", type=Path)
        parser.add_argument("--partner", required=True)
        parser.add_argument("--operator", required=True, help="Discovery user authorized to change microcourse catalog metadata")
        parser.add_argument("--validate-only", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        users = get_user_model()
        try:
            operator = users.objects.get(**{users.USERNAME_FIELD: options["operator"]})
        except users.DoesNotExist as exc:
            raise CommandError("The Discovery operator does not exist.") from exc
        if not operator.is_active or not operator.has_perm("catalog_extensions.change_microcoursecatalogmetadata"):
            raise CommandError("The operator needs permission to change microcourse catalog metadata.")
        try:
            source = options["export_file"].read_bytes()
            key, plan, approval = approved_course_export(json.loads(source))
        except (OSError, ValueError, TypeError) as exc:
            raise CommandError(str(exc)) from exc
        try:
            metadata = MicrocourseCatalogMetadata.objects.select_for_update().get(
                course_run__key=key,
                course_run__course__partner__short_code=options["partner"],
            )
        except MicrocourseCatalogMetadata.DoesNotExist as exc:
            raise CommandError("Matching course catalog metadata is missing for this partner.") from exc
        existing = metadata.credit_plan or {}
        if existing.get("version", 0) > plan["version"]:
            raise CommandError("A newer credit plan is already present in Discovery.")
        if existing.get("status") == "approved" and existing.get("version") == plan["version"]:
            if existing != plan:
                raise CommandError("Approved plan versions cannot be replaced with different content.")
            self.stdout.write("Approved credit plan is already synchronized.")
            return
        if options["validate_only"]:
            self.stdout.write("Approved credit export is valid; no writes.")
            return
        metadata.credit_plan = plan
        metadata.authoring_metadata = {
            **metadata.authoring_metadata,
            "credit_plan_source": {
                "sha256": hashlib.sha256(source).hexdigest(),
                "approval": approval, "operator_id": operator.pk,
                "synced_at": timezone.now().isoformat(),
            },
        }
        metadata.save(update_fields=["credit_plan", "authoring_metadata"])
        self.stdout.write("Approved planned credits synchronized. Catalog publication flags were not changed.")

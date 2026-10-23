from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog_extensions.models.program import CertificateProgramCatalogMetadata
from catalog_extensions.services.credit_contract import approved_program_budget


class Command(BaseCommand):
    help = "Approve a complete whole-program credit budget; does not publish the program or award learner credits."

    def add_arguments(self, parser):
        parser.add_argument("program_code")
        parser.add_argument("--partner", required=True)
        parser.add_argument("--operator", required=True)
        parser.add_argument("--validate-only", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        users = get_user_model()
        try:
            operator = users.objects.get(**{users.USERNAME_FIELD: options["operator"]})
            metadata = CertificateProgramCatalogMetadata.objects.select_for_update().get(
                program_code=options["program_code"], program__partner__short_code=options["partner"],
            )
        except (users.DoesNotExist, CertificateProgramCatalogMetadata.DoesNotExist) as exc:
            raise CommandError("The operator or partner-scoped program does not exist.") from exc
        if not operator.is_active or not operator.has_perm("catalog_extensions.approve_program_credit_plan"):
            raise CommandError("The operator needs certificate-program credit-plan approval permission.")
        requirements = list(metadata.program.cba_course_requirements.filter(required=True).select_related("course_run__cba_catalog"))
        actual = {str(item.course_run.key) for item in requirements}
        source = metadata.authoring_metadata.get("source_record", {})
        expected = {
            item["course_key"] for item in source.get("microcourses", [])
            if isinstance(item, dict) and item.get("required", True) and "course_key" in item
        }
        if expected - actual:
            raise CommandError("Required program memberships are missing: " + ", ".join(sorted(expected - actual)))
        try:
            plan = approved_program_budget(
                metadata.credit_plan,
                [item.course_run.cba_catalog.credit_plan for item in requirements],
                has_electives=bool(metadata.elective_groups),
            )
        except (ValueError, TypeError, ObjectDoesNotExist) as exc:
            raise CommandError(str(exc)) from exc
        if metadata.credit_plan.get("status") == "approved":
            self.stdout.write("Program credit budget is already approved.")
            return
        if options["validate_only"]:
            self.stdout.write("Program credit budget is complete; no writes.")
            return
        metadata.credit_plan = plan
        metadata.authoring_metadata = {
            **metadata.authoring_metadata,
            "program_credit_approval": {
                "operator_id": operator.pk, "approved_at": timezone.now().isoformat(),
                "version": plan["version"], "required_course_keys": sorted(actual),
            },
        }
        metadata.save(update_fields=["credit_plan", "authoring_metadata"])
        self.stdout.write("Program credit budget approved. Publication flags were not changed.")

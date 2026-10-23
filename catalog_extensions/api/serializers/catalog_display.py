"""Explicit public display fields for the Wagtail catalog."""

from rest_framework import serializers

from catalog_extensions.models.course import MicrocourseCatalogMetadata
from catalog_extensions.models.program import CertificateProgramCatalogMetadata
from catalog_extensions.services.credit_contract import credit_summary


COMMON_DISPLAY_FIELDS = tuple("""
owning_organization listing_organizations site_keys publication_ready
content_version updated_at price currency learning_credits
""".split())

COURSE_DISPLAY_FIELDS = tuple("""
record_type marketing_slug target_audience prerequisite_course_keys
recommended_prerequisites level delivery_format language assessment_summary
completion_requirements takeaway credential enrollment_url waitlist_url
syllabus_url parent_course sequence_in_course standards_alignment
""".split())

PROGRAM_DISPLAY_FIELDS = tuple("""
duration_minutes_min duration_minutes_max microcourse_price ksa weeks
elective_groups target_audience roles_prepared_for entry_requirements
work_products capstone examination exam_blueprint certificate_term
award_title standards_alignment sample_work_url enrollment_url waitlist_url
""".split())


class CreditDisplaySerializer(serializers.ModelSerializer):
    learning_credits = serializers.SerializerMethodField()

    def get_learning_credits(self, obj):
        return credit_summary(getattr(obj, "credit_plan", {}), self.credit_kind)


class CourseDisplayMetadataSerializer(CreditDisplaySerializer):
    credit_kind = "microcourse"
    owning_organization = serializers.SlugRelatedField(
        slug_field="key", read_only=True, allow_null=True,
    )
    listing_organizations = serializers.SlugRelatedField(
        slug_field="key", read_only=True, many=True,
    )

    class Meta:
        model = MicrocourseCatalogMetadata
        fields = COMMON_DISPLAY_FIELDS + COURSE_DISPLAY_FIELDS
        read_only_fields = fields


class ProgramDisplayMetadataSerializer(CreditDisplaySerializer):
    credit_kind = "program"
    owning_organization = serializers.SlugRelatedField(
        slug_field="key", read_only=True, allow_null=True,
    )
    listing_organizations = serializers.SlugRelatedField(
        slug_field="key", read_only=True, many=True,
    )

    class Meta:
        model = CertificateProgramCatalogMetadata
        fields = COMMON_DISPLAY_FIELDS + PROGRAM_DISPLAY_FIELDS
        read_only_fields = fields

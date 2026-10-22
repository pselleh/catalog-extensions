"""Explicit public display fields for the Wagtail catalog."""

from rest_framework import serializers

from catalog_extensions.models.course import MicrocourseCatalogMetadata
from catalog_extensions.models.program import CertificateProgramCatalogMetadata


COMMON_DISPLAY_FIELDS = tuple("""
owning_organization listing_organizations site_keys publication_ready
content_version updated_at price currency
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


class CourseDisplayMetadataSerializer(serializers.ModelSerializer):
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


class ProgramDisplayMetadataSerializer(serializers.ModelSerializer):
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

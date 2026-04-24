from django.contrib import admin
from .models import (
    CourseAccreditationMetadata,
    ProgramAccreditationMetadata,
    LearnerCourseCreditRecord,
)


@admin.register(CourseAccreditationMetadata)
class CourseAccreditationMetadataAdmin(admin.ModelAdmin):
    list_display = ("course_key", "ceu_value", "pdu_value", "is_accreditation_approved")
    search_fields = ("course_key", "accrediting_body", "credit_text")
    list_filter = ("is_accreditation_approved",)


@admin.register(ProgramAccreditationMetadata)
class ProgramAccreditationMetadataAdmin(admin.ModelAdmin):
    list_display = ("program_uuid", "ceu_total", "pdu_total", "is_accreditation_approved")
    search_fields = ("program_uuid", "accrediting_body", "credit_text")
    list_filter = ("is_accreditation_approved",)


@admin.register(LearnerCourseCreditRecord)
class LearnerCourseCreditRecordAdmin(admin.ModelAdmin):
    list_display = ("user_id", "course_key", "ceu_awarded", "pdu_awarded", "awarded_at")
    search_fields = ("user_id", "course_key", "source_certificate_uuid")

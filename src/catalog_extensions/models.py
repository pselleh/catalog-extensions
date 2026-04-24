from django.db import models


class CourseAccreditationMetadata(models.Model):
    course_key = models.CharField(max_length=255, unique=True, db_index=True)

    ceu_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ceu_label = models.CharField(max_length=50, default="CEU", blank=True)

    pdu_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pdu_label = models.CharField(max_length=50, default="PDU", blank=True)

    credit_text = models.CharField(max_length=255, blank=True)
    accrediting_body = models.CharField(max_length=255, blank=True)
    transcript_display_text = models.CharField(max_length=255, blank=True)

    learning_outcomes = models.JSONField(default=list, blank=True)
    syllabus = models.JSONField(default=list, blank=True)
    prerequisites = models.JSONField(default=list, blank=True)
    references = models.JSONField(default=list, blank=True)
    topics = models.JSONField(default=list, blank=True)

    transcript_language = models.CharField(max_length=50, blank=True)
    duration_text = models.CharField(max_length=100, blank=True)

    category_label = models.CharField(max_length=100, blank=True)
    delivery_mode = models.CharField(max_length=50, default="ONLINE", blank=True)
    price_text = models.CharField(max_length=50, blank=True)
    availability_text = models.CharField(max_length=50, blank=True)

    is_accreditation_approved = models.BooleanField(default=False)
    accreditation_version = models.CharField(max_length=50, blank=True)
    effective_start = models.DateField(null=True, blank=True)
    effective_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.course_key


class ProgramAccreditationMetadata(models.Model):
    program_uuid = models.UUIDField(unique=True, db_index=True)

    ceu_total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    pdu_total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    credit_text = models.CharField(max_length=255, blank=True)
    accrediting_body = models.CharField(max_length=255, blank=True)

    learning_outcomes = models.JSONField(default=list, blank=True)
    syllabus = models.JSONField(default=list, blank=True)
    prerequisites = models.JSONField(default=list, blank=True)
    references = models.JSONField(default=list, blank=True)
    topics = models.JSONField(default=list, blank=True)

    duration_text = models.CharField(max_length=100, blank=True)
    transcript_language = models.CharField(max_length=50, blank=True)

    category_label = models.CharField(max_length=100, blank=True)
    delivery_mode = models.CharField(max_length=50, default="ONLINE", blank=True)
    price_text = models.CharField(max_length=50, blank=True)
    availability_text = models.CharField(max_length=50, blank=True)

    is_accreditation_approved = models.BooleanField(default=False)
    accreditation_version = models.CharField(max_length=50, blank=True)
    effective_start = models.DateField(null=True, blank=True)
    effective_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.program_uuid)


class LearnerCourseCreditRecord(models.Model):
    user_id = models.IntegerField(db_index=True)
    course_key = models.CharField(max_length=255, db_index=True)

    ceu_awarded = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pdu_awarded = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    awarded_at = models.DateTimeField(auto_now=True)

    source_certificate_uuid = models.CharField(max_length=255, blank=True)
    credit_text = models.CharField(max_length=255, blank=True)
    accrediting_body = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("user_id", "course_key")

    def __str__(self):
        return f"{self.user_id} - {self.course_key}"

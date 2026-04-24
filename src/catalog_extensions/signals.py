from django.dispatch import receiver

from .models import CourseAccreditationMetadata, LearnerCourseCreditRecord

try:
    from certificates.signals import certificate_issued
except Exception:
    certificate_issued = None


if certificate_issued:
    @receiver(certificate_issued)
    def award_credit(sender, user, course_id, **kwargs):
        meta = CourseAccreditationMetadata.objects.filter(course_key=str(course_id)).first()
        if not meta:
            return

        LearnerCourseCreditRecord.objects.update_or_create(
            user_id=user.id,
            course_key=str(course_id),
            defaults={
                "ceu_awarded": meta.ceu_value,
                "pdu_awarded": meta.pdu_value,
                "credit_text": meta.transcript_display_text or meta.credit_text,
                "accrediting_body": meta.accrediting_body,
            },
        )

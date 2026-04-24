from .models import LearnerCourseCreditRecord


def get_transcript(user_id):
    records = LearnerCourseCreditRecord.objects.filter(user_id=user_id).order_by("-awarded_at")

    return [
        {
            "courseKey": record.course_key,
            "courseTitle": record.course_key,
            "completionDate": record.awarded_at,
            "grade": "",
            "certificateStatus": "Issued",
            "ceuAwarded": record.ceu_awarded,
            "pduAwarded": record.pdu_awarded,
            "accreditingBody": record.accrediting_body,
            "transcriptDisplayText": record.credit_text,
        }
        for record in records
    ]

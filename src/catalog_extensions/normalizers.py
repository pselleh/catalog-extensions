import bleach

from .models import CourseAccreditationMetadata
from .services import compute_is_available


def normalize_course(course, hubspot_source="catalog"):
    meta = CourseAccreditationMetadata.objects.filter(course_key=str(course.key)).first()
    is_available = compute_is_available(course)

    return {
        "key": str(course.key),
        "title": getattr(course, "title", "") or "",
        "shortDescription": getattr(course, "short_description", "") or "",
        "fullDescriptionHtml": bleach.clean(getattr(course, "full_description", "") or ""),
        "imageUrl": getattr(course, "image_url", "") or "",
        "videoUrl": getattr(getattr(course, "video", None), "src", None) if getattr(course, "video", None) else None,
        "pacingType": getattr(course, "pacing_type", "") or "",
        "start": getattr(course, "start", None),
        "end": getattr(course, "end", None),
        "enrollmentStart": getattr(course, "enrollment_start", None),
        "enrollmentEnd": getattr(course, "enrollment_end", None),
        "effort": getattr(course, "effort", "") or "",
        "language": getattr(course, "language", "") or "",
        "subjects": [subject.name for subject in course.subjects.all()] if hasattr(course, "subjects") else [],
        "instructors": [
            {
                "name": staff.get("name"),
                "bio": staff.get("bio"),
                "imageUrl": staff.get("profile_image_url"),
            }
            for staff in (getattr(course, "staff", []) or [])
        ],

        "categoryLabel": getattr(meta, "category_label", "") if meta else "",
        "deliveryMode": getattr(meta, "delivery_mode", "ONLINE") if meta else "ONLINE",
        "durationText": getattr(meta, "duration_text", "") if meta else "",
        "availabilityText": (
            getattr(meta, "availability_text", "")
            if meta and getattr(meta, "availability_text", "")
            else ("AVAILABLE NOW" if is_available else "JOIN WAITLIST")
        ),

        "price": None,
        "priceText": getattr(meta, "price_text", "") if meta else "",
        "currency": "USD",

        "isAvailable": is_available,
        "waitlistEnabled": not is_available,

        "credit": {
            "ceu": getattr(meta, "ceu_value", None) if meta else None,
            "ceuLabel": getattr(meta, "ceu_label", "CEU") if meta else "CEU",
            "pdu": getattr(meta, "pdu_value", None) if meta else None,
            "pduLabel": getattr(meta, "pdu_label", "PDU") if meta else "PDU",
            "creditText": getattr(meta, "credit_text", None) if meta else None,
            "accreditingBody": getattr(meta, "accrediting_body", None) if meta else None,
            "transcriptDisplayText": getattr(meta, "transcript_display_text", None) if meta else None,
        },

        "learningOutcomes": getattr(meta, "learning_outcomes", []) if meta else [],
        "syllabus": getattr(meta, "syllabus", []) if meta else [],
        "prerequisites": getattr(meta, "prerequisites", []) if meta else [],
        "references": getattr(meta, "references", []) if meta else [],
        "topics": getattr(meta, "topics", []) if meta else [],
        "transcriptLanguage": getattr(meta, "transcript_language", "") if meta else "",

        "hubspotContext": {
            "itemType": "course",
            "itemId": str(course.key),
            "itemTitle": getattr(course, "title", "") or "",
            "price": None,
            "currency": "USD",
            "source": hubspot_source,
        },
    }

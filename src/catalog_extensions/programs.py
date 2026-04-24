import bleach

from .models import ProgramAccreditationMetadata


def normalize_program(program, hubspot_source="catalog"):
    meta = ProgramAccreditationMetadata.objects.filter(program_uuid=program.uuid).first()

    included_courses = []
    if hasattr(program, "courses"):
        for course in program.courses.all():
            included_courses.append(
                {
                    "key": str(course.key),
                    "title": getattr(course, "title", "") or "",
                    "shortDescription": getattr(course, "short_description", "") or "",
                    "imageUrl": getattr(course, "image_url", "") or "",
                }
            )

    return {
        "uuid": str(program.uuid),
        "title": getattr(program, "title", "") or "",
        "subtitle": getattr(program, "subtitle", "") or "",
        "imageUrl": getattr(program, "card_image_url", "") or "",
        "fullDescriptionHtml": bleach.clean(getattr(program, "full_description", "") or ""),
        "includedCourses": included_courses,

        "categoryLabel": getattr(meta, "category_label", "") if meta else "",
        "deliveryMode": getattr(meta, "delivery_mode", "ONLINE") if meta else "ONLINE",
        "durationText": getattr(meta, "duration_text", "") if meta else "",
        "availabilityText": getattr(meta, "availability_text", "JOIN WAITLIST") if meta else "JOIN WAITLIST",

        "price": None,
        "priceText": getattr(meta, "price_text", "") if meta else "",
        "currency": "USD",

        "waitlistEnabled": True,

        "credit": {
            "ceu": getattr(meta, "ceu_total", None) if meta else None,
            "pdu": getattr(meta, "pdu_total", None) if meta else None,
            "creditText": getattr(meta, "credit_text", None) if meta else None,
            "accreditingBody": getattr(meta, "accrediting_body", None) if meta else None,
        },

        "learningOutcomes": getattr(meta, "learning_outcomes", []) if meta else [],
        "syllabus": getattr(meta, "syllabus", []) if meta else [],
        "prerequisites": getattr(meta, "prerequisites", []) if meta else [],
        "references": getattr(meta, "references", []) if meta else [],
        "topics": getattr(meta, "topics", []) if meta else [],
        "transcriptLanguage": getattr(meta, "transcript_language", "") if meta else "",

        "hubspotContext": {
            "itemType": "program",
            "itemId": str(program.uuid),
            "itemTitle": getattr(program, "title", "") or "",
            "price": None,
            "currency": "USD",
            "source": hubspot_source,
        },
    }

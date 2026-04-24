from django.utils.timezone import now


def compute_is_available(course):
    current = now()

    if getattr(course, "enrollment_start", None) and getattr(course, "enrollment_end", None):
        return course.enrollment_start <= current <= course.enrollment_end

    return getattr(course, "availability", "") == "current"

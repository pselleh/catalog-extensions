from django.core.validators import MinValueValidator
from django.db import models

from catalog_extensions.models.catalog_contract import CatalogContractMetadata

from course_discovery.apps.course_metadata.models import CourseRun, Person


class CatalogStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PLANNED = "planned", "Planned"
    WAITLIST_OPEN = "waitlist_open", "Waitlist open"
    ENROLLMENT_OPEN = "enrollment_open", "Enrollment open"
    ENROLLMENT_CLOSED = "enrollment_closed", "Enrollment closed"
    ARCHIVED = "archived", "Archived"


class CatalogVisibility(models.TextChoices):
    PUBLIC = "public", "Public"
    HIDDEN = "hidden", "Hidden"


class AccessScope(models.TextChoices):
    PUBLIC = "public", "Public"
    ORGANIZATION_CODE = "organization_code", "Organization code"
    PROGRAM_ONLY = "program_only", "Certificate program only"


class FacultyRole(models.TextChoices):
    PROGRAM_DIRECTOR = "program_director", "Program Director"
    LEAD_SUBJECT_MATTER_EXPERT = "lead_sme", "Lead Subject-Matter Expert"
    INSTRUCTOR = "instructor", "Instructor"
    FACILITATOR = "facilitator", "Facilitator"
    COURSE_AUTHOR = "course_author", "Course Author"
    TECHNICAL_REVIEWER = "technical_reviewer", "Technical Reviewer"


class MicrocourseCatalogMetadata(CatalogContractMetadata):
    """CBA catalog fields that are not represented by native Discovery fields."""

    record_type = models.CharField(max_length=32, default="microcourse", choices=[("microcourse", "Microcourse"), ("program_hub", "Program hub"), ("capstone", "Capstone"), ("examination", "Examination")])
    marketing_slug = models.SlugField(max_length=255, blank=True)
    target_audience = models.TextField(blank=True)
    prerequisite_course_keys = models.JSONField(default=list, blank=True)
    recommended_prerequisites = models.JSONField(default=list, blank=True)
    level = models.CharField(max_length=64, blank=True)
    delivery_format = models.CharField(max_length=128, blank=True)
    language = models.CharField(max_length=32, blank=True)
    assessment_summary = models.TextField(blank=True)
    completion_requirements = models.TextField(blank=True)
    takeaway = models.TextField(blank=True)
    credential = models.TextField(blank=True)
    enrollment_url = models.URLField(max_length=2048, null=True, blank=True)
    waitlist_url = models.URLField(max_length=2048, null=True, blank=True)
    syllabus_url = models.URLField(max_length=2048, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=None, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    parent_course = models.CharField(max_length=128, blank=True)
    sequence_in_course = models.PositiveIntegerField(null=True, blank=True)
    standards_alignment = models.JSONField(default=list, blank=True)


    course_run = models.OneToOneField(
        CourseRun,
        on_delete=models.CASCADE,
        related_name="cba_catalog",
    )
    primary_catalog_category = models.ForeignKey(
        "catalog_extensions.CatalogCategory",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="primary_microcourses",
    )
    catalog_categories = models.ManyToManyField(
        "catalog_extensions.CatalogCategory",
        blank=True,
        related_name="microcourses",
    )
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, default=None, validators=[MinValueValidator(1)])
    catalog_status = models.CharField(
        max_length=32,
        choices=CatalogStatus.choices,
        default=CatalogStatus.DRAFT,
        db_index=True,
    )
    catalog_visibility = models.CharField(
        max_length=16,
        choices=CatalogVisibility.choices,
        default=CatalogVisibility.PUBLIC,
        db_index=True,
    )
    access_scope = models.CharField(
        max_length=32,
        choices=AccessScope.choices,
        default=AccessScope.PUBLIC,
        db_index=True,
    )
    access_policy_key = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
        help_text="Stable Wagtail policy identifier; never store an organization code here.",
    )
    standalone_enrollment_allowed = models.BooleanField(default=True)
    course_overview = models.TextField(blank=True)
    image_alt = models.CharField(max_length=255, blank=True)
    learning_outcomes = models.JSONField(default=list, blank=True)
    references = models.JSONField(default=list, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "CBA microcourse catalog metadata"
        verbose_name_plural = "CBA microcourse catalog metadata"
        permissions = [
            ("view_restricted_catalog", "Can view the restricted CBA catalog"),
        ]

    def __str__(self):
        return str(self.course_run.key)


class CourseRunFacultyAssignment(models.Model):
    """Public-facing course faculty; separate from Studio course-team permissions."""

    course_run = models.ForeignKey(
        CourseRun,
        on_delete=models.CASCADE,
        related_name="cba_faculty_assignments",
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="cba_course_assignments",
    )
    role = models.CharField(
        max_length=32,
        choices=FacultyRole.choices,
        default=FacultyRole.INSTRUCTOR,
    )
    credentials = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("course_run", "person", "role"),
                name="cba_unique_course_run_person_role",
            )
        ]

    def __str__(self):
        return f"{self.person.full_name} — {self.get_role_display()}"

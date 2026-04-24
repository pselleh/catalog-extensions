from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from course_discovery.apps.api.v1.models import Course
from course_discovery.apps.programs.models import Program

from .normalizers import normalize_course
from .pagination import paginate
from .programs import normalize_program
from .transcript import get_transcript


@method_decorator(cache_page(60 * 5), name="dispatch")
class CourseListView(APIView):
    def get(self, request):
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 15))

        courses = Course.objects.filter(pacing_type="self_paced").prefetch_related("subjects")
        normalized = [normalize_course(course, hubspot_source="catalog") for course in courses]

        return Response(paginate(normalized, page, page_size))


@method_decorator(cache_page(60 * 5), name="dispatch")
class ProgramListView(APIView):
    def get(self, request):
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 15))

        programs = Program.objects.prefetch_related("courses")
        normalized = [normalize_program(program, hubspot_source="catalog") for program in programs]

        return Response(paginate(normalized, page, page_size))


@method_decorator(cache_page(60 * 5), name="dispatch")
class CourseDetailView(APIView):
    def get(self, request, course_key):
        course = get_object_or_404(Course.objects.prefetch_related("subjects"), key=course_key)
        return Response(normalize_course(course, hubspot_source="course_detail"))


@method_decorator(cache_page(60 * 5), name="dispatch")
class ProgramDetailView(APIView):
    def get(self, request, uuid):
        program = get_object_or_404(Program.objects.prefetch_related("courses"), uuid=uuid)
        return Response(normalize_program(program, hubspot_source="program_detail"))


class TranscriptView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(get_transcript(request.user.id))

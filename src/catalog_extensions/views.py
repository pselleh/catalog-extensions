from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404

from course_discovery.apps.course_metadata.models import Course
from course_discovery.apps.programs.models import Program


# -----------------------------------
# COURSE LIST
# -----------------------------------
class CourseListView(APIView):

    def get(self, request):
        courses = Course.objects.all()[:10]

        results = [
            {
                "key": str(c.key),
                "title": c.title,
            }
            for c in courses
        ]

        return Response({
            "count": len(results),
            "results": results
        })


# -----------------------------------
# COURSE DETAIL
# -----------------------------------
class CourseDetailView(APIView):

    def get(self, request, course_key):
        course = get_object_or_404(Course, key=course_key)

        return Response({
            "key": str(course.key),
            "title": course.title,
        })


# -----------------------------------
# PROGRAM LIST
# -----------------------------------
class ProgramListView(APIView):

    def get(self, request):
        programs = Program.objects.all()[:10]

        results = [
            {
                "uuid": str(p.uuid),
                "title": p.title,
            }
            for p in programs
        ]

        return Response({
            "count": len(results),
            "results": results
        })


# -----------------------------------
# PROGRAM DETAIL
# -----------------------------------
class ProgramDetailView(APIView):

    def get(self, request, uuid):
        program = get_object_or_404(Program, uuid=uuid)

        return Response({
            "uuid": str(program.uuid),
            "title": program.title,
        })


# -----------------------------------
# TRANSCRIPT
# -----------------------------------
class TranscriptView(APIView):

    def get(self, request):
        return Response({
            "results": []
        })

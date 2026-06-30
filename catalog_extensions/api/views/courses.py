from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog_extensions.api.serializers import UnifiedCourseSerializer
from catalog_extensions.services.course_service import CourseService


class UnifiedCatalogView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        courses = CourseService().list_courses(limit=100)

        serializer = UnifiedCourseSerializer(
            [
                {
                    "key": str(course.key),
                    "title": course.title or "",
                    "short_description": course.short_description or "",
                    "marketing_url": course.marketing_url or "",
                }
                for course in courses
            ],
            many=True,
        )

        return Response(
            {
                "count": len(serializer.data),
                "results": serializer.data,
            }
        )

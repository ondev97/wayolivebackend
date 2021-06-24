import django_filters
from django.db.models import Q
from .models import Event


class EventFilter(django_filters.FilterSet):
    search = django_filters.NumberFilter(method='custom_search')

    class Meta:
        model = Event
        fields = ['search']

    def custom_search(self,queryset,name,value):
        return queryset.filter(
            Q(event_mode__id=value)
        )

# class CourseFilter(django_filters.FilterSet):
#     search = django_filters.CharFilter(method='custom_search')
#
#     class Meta:
#         model = Course
#         fields = ['search']
#
#     def custom_search(self,queryset,name,value):
#         return queryset.filter(
#             Q(course_name__icontains=value)
#         )


# class EnrollCourseFilter(django_filters.FilterSet):
#     search = django_filters.CharFilter(method='custom_search')
#
#     class Meta:
#         model = Enrollment
#         fields = ['search']
#
#     def custom_search(self,queryset,name,value):
#         return queryset.filter(
#             Q(course__course_name__icontains = value)
#         )
import django_filters
from django.db.models import Q
from .models import Event


class EventFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(method='category_search')
    type = django_filters.CharFilter(method='type_search')

    class Meta:
        model = Event
        fields = ['category', 'type']

    def category_search(self,queryset,name,value):
        return queryset.filter(
            Q(event_mode__event_mode_name__icontains=value)
        )

    def type_search(self,queryset,name,value):
        return queryset.filter(
            Q(event_type__icontains=value)
        )


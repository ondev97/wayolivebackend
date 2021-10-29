import django_filters
from django.db.models import Q

from .models import UserProfile


class UserProfileFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='user_search')

    class Meta:
        model = UserProfile
        fields = ['search']

    def user_search(self, queryset, name, value):
        return queryset.filter(
            Q(user__username__icontains=value) | Q(user__first_name__icontains=value) | Q(user__last_name__icontains=value) | Q(user__email__icontains=value)
        )


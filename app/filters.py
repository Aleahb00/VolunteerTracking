import django_filters
from .models import *

class VolunteerFilter(django_filters.FilterSet):
    skilled_worker = django_filters.ChoiceFilter(
        field_name='confirmed_skilled_worker',
        choices=((True, 'Marked'), (False, 'Unmarked')),
        label='Marked Skilled Worker',
    )
    order_by = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('name', 'name'),
            ('date_of_work', 'date_of_work'),
        ),
        label='Sort By',
    )
    

    class Meta:
        model = Volunteer
        fields = ['skilled_worker', 'order_by']
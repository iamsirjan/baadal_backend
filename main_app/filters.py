from django_filters import FilterSet, NumberFilter
from .models import Product


class ProductFilter(FilterSet):
    user = NumberFilter(field_name='user__user_id')

    class Meta:
        model = Product
        fields = ['user']

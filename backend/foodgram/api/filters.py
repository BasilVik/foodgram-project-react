from django_filters.rest_framework import (BooleanFilter, Filter, FilterSet,
                                           ModelMultipleChoiceFilter)
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = Filter(
        method='filter_author'
    )

    class Meta:
        model = Recipe
        fields = ('tags',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_list(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset

    def filter_author(self, queryset, name, value):
        if value == 'me':
            return queryset.filter(author=self.request.user)
        return queryset.filter(author=value)

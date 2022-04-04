from django_filters import rest_framework as filter

from .models import Ingredient, Recipe


class RecipeFilter(filter.FilterSet):
    """Фильтр для модели Recipe
    """

    tags = filter.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filter.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filter.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'is_favorited', 'tags', 'is_in_shopping_cart',)

    def get_is_favorited(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(in_favorites__user=self.request.user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(in_shopping_cart__user=self.request.user)


class IngredientSearchFilter(filter.FilterSet):
    """Фильтр для модели Ingredient
    """

    name = filter.CharFilter(method='search_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(name__startswith=value)

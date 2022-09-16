from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingList, Tag)
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated

from .filters import RecipeFilter
from .mixins import ListRetrieveViewSet
from .pagination import PageLimitPagination
from .permissions import IsAuthenticatedAuthorOrReadOnly
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer
from .utils import create_delete_recipes_list


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedAuthorOrReadOnly,)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(request.method)
        return super().update(request, *args, **kwargs)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return create_delete_recipes_list(request, pk, Favorite)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return create_delete_recipes_list(request, pk, ShoppingList)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shop_list = {}
        ingredients = IngredientAmount.objects.filter(
            recipe__in=request.user.shopping_list.values('recipe')
        ).select_related('ingredient')

        for obj in ingredients:
            ingredient = obj.ingredient.name
            if ingredient not in shop_list:
                shop_list[ingredient] = {
                    'measurement_unit': obj.ingredient.measurement_unit,
                    'amount': obj.amount
                }
            else:
                shop_list[ingredient]['amount'] += obj.amount
        download_list = f'Список покупок пользователя {request.user.username}:'

        for ingredient in shop_list:
            download_list += (
                f'{ingredient} '
                f'({shop_list[ingredient]["measurement_unit"]}) '
                f'- {shop_list[ingredient]["amount"]}\n'
            )
        response = HttpResponse(
            download_list,
            content_type='text/plain;charset=UTF-8',
        )
        response['Content-Disposition'] = (
            'attachment;'
            'filename="shopping_list.txt"'
        )
        return response

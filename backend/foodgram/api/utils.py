from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from recipes.models import Recipe

def is_in_favorite_or_shop_list(self, obj, model):
    if (
        self.context.get('request') is not None
        and self.context.get('request').user.is_authenticated
    ):
        return model.objects.filter(
            user=self.context.get('request').user, recipe=obj
        ).exists()
    return False


def create_delete_recipes_list(request, pk, model):
    from .serializers import RecipeShortSerializer
    recipe = get_object_or_404(Recipe, id=pk)
    if request.method == 'POST':
        obj, created = model.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if created:
            serializer = RecipeShortSerializer(recipe)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(
            {'errors': 'Рецепт уже добавлен в список!'},
            status=status.HTTP_400_BAD_REQUEST
        )
    obj = model.objects.filter(
        user=request.user, recipe=recipe
    )
    if obj:
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': 'Такого рецепта нет в списке!'},
        status=status.HTTP_400_BAD_REQUEST
    )

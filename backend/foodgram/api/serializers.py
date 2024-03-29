from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingList, Tag)
from rest_framework import serializers
from users.serializers import UserDetailSerializer

from .utils import is_in_favorite_or_shop_list
from .validators import validate_ingredient_amounts


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = serializers.UniqueTogetherValidator(
            queryset=IngredientAmount.objects.all(),
            fields=('recipe', 'ingredient'),
            message='В рецепте уже есть этот ингредиент!'
        )


class TagsField(serializers.PrimaryKeyRelatedField):

    def to_representation(self, value):
        return TagSerializer(value).data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagsField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserDetailSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredient_amounts',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField()

    def get_is_favorited(self, obj):
        return is_in_favorite_or_shop_list(self, obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return is_in_favorite_or_shop_list(self, obj, ShoppingList)

    def create(self, validated_data):
        ingredients = self.initial_data.get('ingredients')
        validate_ingredient_amounts(ingredients)
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **validated_data
        )
        recipe.tags.set(tags)
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.get('ingredients')
        validate_ingredient_amounts(ingredients)
        super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientAmount.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            IngredientAmount.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        instance.save()
        return instance

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

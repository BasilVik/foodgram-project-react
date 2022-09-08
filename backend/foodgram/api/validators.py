from recipes.models import Ingredient
from rest_framework.serializers import ValidationError


def validate_ingredient_amounts(ingredients):
    if not ingredients:
        raise ValidationError('Поле ingredients обязательно для заполнения!.')
    unique_ingridients_list = []
    for ingredient in ingredients:
        if ingredient.get('amount') is None:
            raise ValidationError(
                'Укажите количество ингредиентов в поле amount!'
            )
        if int(ingredient.get('amount')) < 1:
            raise ValidationError(
                'Количество ингредиентов не может быть меньше 1!'
            )
        ingredient_id = ingredient.get('id')
        if ingredient_id in unique_ingridients_list:
            raise ValidationError('Нельзя добавлять одинаковые ингредиенты!')
        unique_ingridients_list.append(ingredient_id)
        if not Ingredient.objects.filter(id=ingredient_id).exists():
            raise ValidationError('Указан несуществующий ингредиент!')

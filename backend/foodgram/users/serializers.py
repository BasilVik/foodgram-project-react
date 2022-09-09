from recipes.models import Recipe
from rest_framework import serializers

from .models import Follow, User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserDetailSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if (
            self.context.get('request') is not None
            and self.context.get('request').user.is_authenticated
        ):
            return Follow.objects.filter(
                user=self.context.get('request').user,
                author=obj
            ).exists()
        return False

    class Meta(UserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )


class SetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        required=True, max_length=150
    )
    current_password = serializers.CharField(
        required=True, max_length=150
    )

    class Meta:
        model = User
        fields = ('new_password', 'current_password')


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user,
            author=obj.author
        ).exists()

    def get_recipes(self, obj):
        from api.serializers import RecipeShortSerializer
        if self.context:
            recipes_limit = self.context['request'].GET.get('recipes_limit')
            if recipes_limit:
                queryset = Recipe.objects.filter(
                    author=obj.author
                )[:int(recipes_limit)]
        else:
            queryset = Recipe.objects.filter(author=obj.author)
        return RecipeShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

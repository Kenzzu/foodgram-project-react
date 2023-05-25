from django.core.validators import MinValueValidator
from django.db import transaction
from recipes.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import UserSerializer

from .custom_fields import Base64ImageField


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Тэг."""
    color = serializers.RegexField(
        regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
    )
    slug = serializers.RegexField(regex=r'^[a-zA-Z]{1}[\w]+$')

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Ингридиент."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredienterializer(serializers.ModelSerializer):
    '''Сериалайзер для связки ингредиента и количества'''
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientAddSerializer(serializers.ModelSerializer):
    '''Ингредиент и количество для рецепта'''
    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=1, validators=[
            MinValueValidator(1, "Количество должно быть больше 0.")]
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериалайзер для запроса GET модели Рецепт."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(
        read_only=True
    )
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients')
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        ingredients = AmountIngredient.objects.filter(recipe=obj)
        serializer = AmountIngredienterializer(ingredients, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        return (Favorite.objects.filter(
                user=self.context.get('request').user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        '''Проверка рецепта на наличие в списке покупок'''
        request = self.context.get('request')
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для запроса POST модели Рецепт."""
    id = serializers.ReadOnlyField()
    ingredients = IngredientAddSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        min_value=1, validators=[MinValueValidator(
            1, "Количество должно быть больше 0.")])

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    @transaction.atomic
    def tags_and_ingredients_set(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        AmountIngredient.objects.bulk_create(
            [AmountIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.tags_and_ingredients_set(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        AmountIngredient.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()).delete()
        self.tags_and_ingredients_set(instance, tags, ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance,
                                    context=self.context).data

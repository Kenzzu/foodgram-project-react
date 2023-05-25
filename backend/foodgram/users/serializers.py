from api.custom_fields import Base64ImageField
from django.core.validators import MinLengthValidator, RegexValidator
from recipes.models import Recipe
from rest_framework import serializers

from .custom_fields import IsSubscribedField, RecipeCount
from .models import User
from .validators import email_validation, name_validation, username_validation


class UserSerializer(serializers.ModelSerializer):
    '''Сериалайзер для Юзеров'''
    email = serializers.EmailField(max_length=254)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150
    )
    first_name = serializers.CharField(
        max_length=150, validators=[name_validation]
    )
    last_name = serializers.CharField(
        max_length=150, validators=[name_validation]
    )
    is_subscribed = IsSubscribedField(source='*')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user
        if user.is_anonymous:
            del fields['is_subscribed']

        return fields


class SignUpSerializer(serializers.ModelSerializer):
    '''Сериалайзер для создлания Юзера'''
    email = serializers.EmailField(
        max_length=254,
        validators=[email_validation]
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        validators=[username_validation],
        max_length=150
    )
    first_name = serializers.CharField(
        max_length=150, validators=[name_validation]
    )
    last_name = serializers.CharField(
        max_length=150, validators=[name_validation]
    )
    password = serializers.CharField(
        max_length=150,
        write_only=True,
        validators=[
            MinLengthValidator(
                8, "Пароль должен содержать не менее 8 символов."),
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d).+$',
                message="Пароль должен содержать как минимум "
                "одну букву и одну цифру.")]
                )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserSelfSerializer(serializers.ModelSerializer):
    '''Сериалайзер для своей страницы'''
    first_name = serializers.CharField(
        max_length=150,
    )
    last_name = serializers.CharField(
        max_length=150,
    )
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150
    )
    is_subscribed = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


# class TokenSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     email = serializers.EmailField()
#     class Meta:
#         model = User
#         fields = ('password', 'email')


class PasswordSerializer(serializers.Serializer):
    '''Сериалайзер для смены пароля'''
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('current_password', 'new_password')


class RecipeForFlollowSerializer(serializers.ModelSerializer):
    '''Сериалайзер для отображения рецепта при запросах
       связаных с подпиской(+ корзина)'''
    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class FollowReadSerializer(serializers.ModelSerializer):
    '''Сериалайзер для GET-запросов к модели Подписка'''
    is_subscribed = IsSubscribedField(source='*')
    recipes = RecipeForFlollowSerializer(many=True, read_only=True)
    recipes_count = RecipeCount(source='*')

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')


class FollowWriteSerializer(serializers.ModelSerializer):
    '''Сериалайзер для POST-запросов к модели Подписка'''
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = IsSubscribedField(source='*', required=False)
    recipes = RecipeForFlollowSerializer(many=True, read_only=True)
    recipes_count = RecipeCount(source='*', required=False)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

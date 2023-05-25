from django.db import models
from foodgram.settings import AUTH_USER_MODEL

CHARACTER_SLICE = 20


class Tag(models.Model):
    '''Модель Тэг'''
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Тэг'
        )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в HEX'
        )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return f'Тэг {self.name[:CHARACTER_SLICE]}'


class Ingredient(models.Model):
    '''Модель Ингридиент'''
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
        )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
        )

    class Meta:
        unique_together = ['name', 'measurement_unit']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self) -> str:
        return f'Ингредиент {self.name[:CHARACTER_SLICE]}'


class Recipe(models.Model):
    """Модель Рецепт"""

    author = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='api/images/recipes/',
        verbose_name='Картинка',
        blank=True,
        null=True,
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipe_ingridients',
        verbose_name='Ингредиенты',
        through='AmountIngredient')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    def __str__(self):
        return f'Рецепт {self.name}'

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date', ]


class AmountIngredient(models.Model):
    '''Модель для связи Ингредиента и его количества в рецепте'''
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество', default=1)

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('ingredient__name',)
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return (f'{self.ingredient.name} {self.amount}'
                f'{self.ingredient.measurement_unit}')


class Favorite(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lover',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        ordering = ('user', 'recipe')

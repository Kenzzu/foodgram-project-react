from django.contrib import admin

from .models import (
    AmountIngredient,
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag)


class AmountIngredientInline(admin.TabularInline):
    model = AmountIngredient
    min_num = 1
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorite_count',)
    list_filter = ('author', 'name', 'tags',)
    inlines = (AmountIngredientInline,)

    @admin.display(description='В избранном')
    def favorite_count(self, obj):
        return obj.favorite.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)


@admin.register(ShoppingCart)
class ShoppingСartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    list_filter = ('user',)

from rest_framework import serializers

from .models import Follow


class IsSubscribedField(serializers.Field):
    def to_representation(self, obj):
        request = self.context.get('request')
        return Follow.objects.filter(user=request.user, author=obj).exists()


class RecipeCount(serializers.Field):
    def to_representation(self, obj):
        return obj.recipes.count()

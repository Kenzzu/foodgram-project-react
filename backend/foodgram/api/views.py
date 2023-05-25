from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.permissions import Admin, AuthUser, Guest
from users.serializers import RecipeForFlollowSerializer

from .filters import IngredientFilter, TagFilter
from .serializers import (AmountIngredient, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    '''Вьюсет для Тэга'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return [Guest() or AuthUser() or Admin()]
        return [Admin()]


class IngridientViewSet(viewsets.ModelViewSet):
    '''Вьюсет для Ингредиента'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return [Guest() or AuthUser() or Admin()]
        return [Admin()]


class RecipeViewSet(viewsets.ModelViewSet):
    '''Вьюсет для Рецепта'''
    queryset = Recipe.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes_by_action = {
        'create': [Admin | AuthUser],
        'retrieve': [Admin | AuthUser | Guest],
        'destroy': [Admin | AuthUser],
        'favorite': [Admin | AuthUser],
        'shopping_cart': [Admin | AuthUser],
        'download_shopping_cart': [Admin | AuthUser],
    }
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagFilter

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def get_permissions(self):
        """Получение прав для разных action."""
        try:
            return [
                perm() for perm in self.permission_classes_by_action[
                    self.action]]
        except KeyError:
            return [perm() for perm in self.permission_classes]

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            try:
                Favorite.objects.create(user=request.user, recipe=recipe)
            except IntegrityError:
                return Response(
                    {'errors':
                     'Вы уже добавляли этот рецепт в избранное'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeForFlollowSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт удалён из избранного!'},
                status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Проверьте метод'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, **kwargs):
        '''Добавление в список покупок'''
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeForFlollowSerializer(
                recipe, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(
                {'errors': 'Этот рецепт уже добавлен!'},
                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт добавлен!'},
                status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Ошибка'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def download_shopping_cart(self, request):
        '''Создания списка покупок'''
        user = request.user
        ingredients = (
            AmountIngredient.objects
            .filter(recipe__recipe_in_cart__user=user)
            .values('ingredient')
            .annotate(total=Sum('amount'))
            .values_list(
                'ingredient__name', 'total', 'ingredient__measurement_unit')
        )
        response = HttpResponse(content_type='application/pdf')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'dejavusans.ttf'))
        canva = canvas.Canvas(response, pagesize=letter)
        canva.setFillColor(colors.HexColor('#E6E6FA'))
        canva.rect(0, 0, letter[0], letter[1], fill=True, stroke=False)
        self.draw_header(canva, user)
        self.draw_body(canva, ingredients)
        self.draw_footer(canva)
        canva.showPage()
        canva.save()
        return response

    def draw_header(self, canva, user):
        x = 40
        y = 760
        canva.setLineWidth(3)
        canva.line(x - 50, y - 10, x + 680, y - 10)
        canva.setFont("DejaVuSans", 30)
        canva.setFillColorRGB(0, 0.5, 1)
        canva.drawString(x, y, f'Список продуктов для {str(user)}')

    def draw_body(self, canva, ingredients):
        x = 20
        y = 720
        i = 1
        line_height = 20
        max_font_size = 14
        canva.setFont("DejaVuSans", max_font_size)
        canva.setFillColor(colors.black)
        for ingredient in ingredients:
            text = '{}. {} - {} {}'.format(i, *ingredient)
            while canva.stringWidth(text) > 400:
                max_font_size -= 1
                canva.setFont("DejaVuSans", max_font_size)
            canva.drawString(x, y, text)
            y -= line_height
            i += 1

    def draw_footer(self, canva):
        x = 40
        y = 40
        canva.line(x - 50, y + 15, x + 680, y + 15)
        canva.setFont('DejaVuSans', 10)
        canva.drawString(x, y, 'Проект: Foodgram')
        canva.drawString(x, y - 20, 'Версия: v1.0')

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

from users.permissions import Admin, AuthUser, Guest
from users.serializers import RecipeForFlollowSerializer

from .filters import IngredientFilter, TagFilter
from .serializers import (
    AmountIngredient,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer,
    RecipeForCartSerializer,
)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для Тэга"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'slug'
    pagination_class = None

    def get_permissions(self):
        if self.request.method == 'GET':
            return [Guest() or AuthUser() or Admin()]
        return [Admin()]


class IngridientViewSet(viewsets.ModelViewSet):
    """Вьюсет для Ингредиента"""
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
    """Вьюсет для Рецепта"""
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
        if self.action in ['list', 'retrieve']:
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
            Favorite.objects.get_or_create(user=request.user, recipe=recipe)
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
        """Добавление в список покупок"""
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeForCartSerializer(
                recipe, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт удалён!'},
                status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Ошибка'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False)
    def download_shopping_cart(self, request):
        """Создания списка покупок"""
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

        self.draw_background(canva)
        self.draw_header(canva, user)
        self.draw_body(canva, ingredients)
        self.draw_footer(canva)
        self.draw_line(canva)
        canva.showPage()
        canva.save()
        return response

    def draw_header(self, canva, user):
        canva.setFillColorRGB(0, 0.5, 1)
        canva.setFont('DejaVuSans', 30)
        canva.drawString(40, 760, f'Список продуктов для {str(user)}')

    def draw_body(self, canva, ingredients):
        x = 20
        y = 720
        i = 1
        line_height = 20
        max_font_size = 14

        canva.setFont('DejaVuSans', max_font_size)
        canva.setFillColor(colors.black)
        for ingredient in ingredients:
            text = '{}. {} - {} {}'.format(i, *ingredient)
            while canva.stringWidth(text) > 400:
                max_font_size -= 1
                canva.setFont('DejaVuSans', max_font_size)
            canva.drawString(x, y, text)
            y -= line_height
            i += 1

    def draw_footer(self, canva):
        canva.setFont('DejaVuSans', 10)
        canva.drawString(40, 50, 'Проект: Foodgram')
        canva.drawString(40, 30, 'Версия: v1.0')

    def draw_line(self, canva):
        canva.setLineWidth(3)
        canva.line(-10, 750, 720, 750)
        canva.line(-10, 65, 720, 65)

    def draw_background(self, canva):
        canva.setFillColor(colors.HexColor('#D1E6FA'))
        canva.rect(0, 0, letter[0], letter[1], fill=True, stroke=False)

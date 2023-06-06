from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny

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

HEADER_FONT_SIZE = 30
BODY_INITIAL_FONT_SIZE = 14
FOOTER_FONT_SIZE = 10
LINE_WIDTH = 3
LINE_HEIGHT = 20
HEADER_X = 40
HEADER_Y = 760
BODY_X = 20
BODY_Y = 720
FOOTER_X = 40
FOOTER_Y_FIRST = 50
FOOTER_Y_SECOND = 30
FILL_COLOR_RED = 0
FILL_COLOR_GREEN = 0.5
FILL_COLOR_BLUE = 1
MAX_TEXT_WIDTH = 400
BODY_INITIAL_INDEX = 1
BODY_INCREMENT_INDEX = 1
FONT_SIZE_DECREMENT = 1
LINE_Y_HEADER = 750
LINE_Y_FOOTER = 65
LINE_X_HEADER_START = -10
LINE_X_HEADER_END = 720
LINE_X_FOOTER_START = -10
LINE_X_FOOTER_END = 720
BACKGROUND_FILL_COLOR = colors.HexColor('#D1E6FA')
BACKGROUND_X = 0
BACKGROUND_Y = 0
BACKGROUND_WIDTH = letter[0]
BACKGROUND_HEIGHT = letter[1]


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
        'list': [AllowAny],
        'retrieve': [Admin | AuthUser | Guest],
        'destroy': [Admin | AuthUser | Guest],
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
        canva.setFillColorRGB(
            FILL_COLOR_RED, FILL_COLOR_GREEN, FILL_COLOR_BLUE)
        canva.setFont('DejaVuSans', HEADER_FONT_SIZE)
        canva.drawString(
            HEADER_X, HEADER_Y, f'Список продуктов для {str(user)}')

    def draw_body(self, canva, ingredients):
        x = BODY_X
        y = BODY_Y
        i = BODY_INITIAL_INDEX
        font_size = BODY_INITIAL_FONT_SIZE

        canva.setFont('DejaVuSans', font_size)
        canva.setFillColor(colors.black)
        for ingredient in ingredients:
            text = '{}. {} - {} {}'.format(i, *ingredient)
            while canva.stringWidth(text) > MAX_TEXT_WIDTH:
                font_size -= FONT_SIZE_DECREMENT
                canva.setFont('DejaVuSans', font_size)
            canva.drawString(x, y, text)
            y -= LINE_HEIGHT
            i += BODY_INCREMENT_INDEX

    def draw_footer(self, canva):
        canva.setFont('DejaVuSans', FOOTER_FONT_SIZE)
        canva.drawString(FOOTER_X, FOOTER_Y_FIRST, 'Проект: Foodgram')
        canva.drawString(FOOTER_X, FOOTER_Y_SECOND, 'Версия: v1.0')

    def draw_line(self, canva):
        canva.setLineWidth(LINE_WIDTH)
        canva.line(
            LINE_X_HEADER_START,
            LINE_Y_HEADER,
            LINE_X_HEADER_END,
            LINE_Y_HEADER)
        canva.line(
            LINE_X_FOOTER_START,
            LINE_Y_FOOTER,
            LINE_X_FOOTER_END,
            LINE_Y_FOOTER)

    def draw_background(self, canva):
        canva.setFillColor(BACKGROUND_FILL_COLOR)
        canva.rect(
            BACKGROUND_X,
            BACKGROUND_Y,
            BACKGROUND_WIDTH,
            BACKGROUND_HEIGHT, fill=True, stroke=False)

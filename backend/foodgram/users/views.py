from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Follow, User
from .permissions import Admin, AuthUser, Guest
from .serializers import (FollowReadSerializer, FollowWriteSerializer,
                          PasswordSerializer, SignUpSerializer,
                          UserSelfSerializer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Получить список всех пользователей или добавить пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes_by_action = {
        'create': [AllowAny],
        'retrieve': [Admin | AuthUser | Guest],
        'set_password': [Admin | AuthUser],
        'me': [Admin | AuthUser],
        'destroy': [Admin],
        'subscriptions': [Admin | AuthUser],
        'subscribe': [Admin | AuthUser],
    }
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def get_permissions(self):
        """Получение прав для разных action."""
        try:
            return [
                perm() for perm in self.permission_classes_by_action[
                    self.action]]
        except KeyError:
            return [perm() for perm in self.permission_classes]

    @action(
            detail=False,
            methods=['post'])
    def set_password(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = PasswordSerializer(data=request.data)
        old_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        serializer.is_valid(raise_exception=True)
        if new_password == old_password:
            return Response(
                {'status': 'Старый и новый пароль должны отличаться'},
                status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(old_password):
            return Response({'status': 'Старый пароль не верен'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.data.get(new_password))
        user.save()
        return Response({'status': 'Пароль успешно изменен'},
                        status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = make_password(
                request.data.get('password'))
            serializer.save(password=password)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.is_valid(raise_exception=True).errors)

    @action(
        detail=False,
        methods=['get']
    )
    def me(self, request):
        user = request.user
        serializer_class = UserSelfSerializer
        if request.method == 'GET':
            serializer = serializer_class(user)
            return Response(serializer.data)
        return ('Досутен только метод GET')

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowReadSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        user = self.request.user

        if request.method == 'POST':
            if author == user:
                return Response({'error': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FollowWriteSerializer(
                author, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Follow, user=request.user,
                              author=author).delete()
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Ошибка отписки'},
                        status=status.HTTP_400_BAD_REQUEST)

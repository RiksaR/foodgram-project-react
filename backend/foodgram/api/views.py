from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Subscription, Tag)
from .pagination import CustomPagination
from .permissions import (IsAdminOrReadOnly, RecipePermission,
                          SubscriptionListPermission)
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeListSerializer, RecipeMinifiedSerializer,
                          SubscriptionListSerializer, SubscriptionSerializer,
                          TagSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Набор представлений для обработки запросов на получение данных
    модели User, создания и удаления подписок
    """

    queryset = User.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'subscribe':
            return SubscriptionSerializer
        return super().get_serializer_class()

    @action(methods=['get', 'delete',], detail=True)
    def subscribe(self, request, id=None):
        user_for_subscriprion_id = int(self.kwargs['id'])
        user_for_subscriprion = get_object_or_404(
            User,
            id=user_for_subscriprion_id,
        )
        user = request.user
        if request.method == 'GET':
            subscriprion = Subscription.objects.create(
                user=user,
                subscriptions=user_for_subscriprion,
            )
            serializer = self.get_serializer(user_for_subscriprion)
            return Response(serializer.data)
        elif request.method == 'DELETE':
            subscriprion = get_object_or_404(
                Subscription,
                user=user,
                subscriptions=user_for_subscriprion,
            )
            subscriprion.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    """Набор представлений для обработки запросов на получение данных 
    модели Tag
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Набор представлений для обработки запросов на получение данных 
    модели Ingredient
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class =IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Набор представлений для обработки запросов на получение данных 
    модели Recipe, добавления рецептов в избранное и список покупок,
    удаления из избранного и списка покупок, скачивания списка покупок
    """

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    http_method_names = ('get', 'post', 'put', 'patch', 'delete',)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (RecipePermission,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return RecipeMinifiedSerializer
        return RecipeCreateUpdateSerializer

    def get_data(self, request, model):
        recipe_id = int(self.kwargs['pk'])
        recipe = get_object_or_404(Recipe, id=recipe_id)
        user = request.user
        if request.method == 'GET':
            model.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data)
        if request.method == 'DELETE':
            searchable_object = get_object_or_404(
                model,
                user=user,
                recipe=recipe,
            )
            searchable_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        return self.get_data(request, Favorite)

    @action(methods=['get', 'delete',], detail=True)
    def shopping_cart(self, request, pk=None):
        return self.get_data(request, ShoppingCart)

    @action(detail=False)
    def download_shopping_cart(self, request):
        items = IngredientInRecipe.objects.select_related(
            'recipe',
            'ingredient',
        )
        items = items.filter(
            recipe__in_shopping_cart__user=request.user,
        )
        items = items.values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount'),
        ).order_by('-total')
        text='\n'.join([
            f"{item['name']} ({item['units']}) - {item['total']}"
            for item in items
        ])
        filename = 'Shopping_cart'
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class SubscriptionListViewSet(viewsets.ModelViewSet):
    """Набор представлений для обработки запросов на получение списка
    подписчиков текущего пользователя
    """

    serializer_class = SubscriptionListSerializer
    permission_classes = (SubscriptionListPermission,)
    pagination_class = CustomPagination

    def get_queryset(self):
        return get_list_or_404(
            User,
            subscribed_to__user = self.request.user,
        )

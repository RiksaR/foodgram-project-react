from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    SubscriptionListViewSet, TagViewSet)

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionListViewSet.as_view({'get': 'list'}),
    ),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

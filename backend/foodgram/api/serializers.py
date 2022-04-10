from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Subscription, Tag)

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользовательской модели User
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'password',)
        extra_kwargs = {"password": {'write_only': True}}

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Subscription.objects.filter(
            user=user,
            subscriptions=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели IngredientInRecipe
    """

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class IngredientInRecipeCreateUpdateSerializer(serializers.Serializer):
    """Сериализатор для модели IngredientInRecipe, работающий с полями
    ingredient.id, amount
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount',)


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода данных объектов модели Recipe
    """

    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set',
        many=True,
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time',)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(
            user=user,
            recipe=obj).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(user=user, recipe=obj).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления объектов модели Recipe
    """

    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = IngredientInRecipeCreateUpdateSerializer(
        many=True,
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',)
    
    def to_representation(self, instance):
        serializer = RecipeListSerializer(instance)
        return serializer.data

    def add_data_to_recipe(self, recipe, tags_data, ingredients_data):
        for tag in tags_data:
            recipe.tags.add(tag)
        for data in ingredients_data:
            IngredientInRecipe.objects.create(
                ingredient=data['id'],
                recipe=recipe,
                amount=data['amount'],
            )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        author = validated_data.get('author')
        name = validated_data.get('name')
        image = validated_data.get('image')
        text = validated_data.get('text')
        cooking_time = validated_data.get('cooking_time')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author = author,
            name=name,
            image=image,
            text=text,
            cooking_time=cooking_time,
        )
        self.add_data_to_recipe(recipe, tags_data, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        super().update(instance, validated_data)
        ingredients_for_delete = IngredientInRecipe.objects.filter(
                recipe=instance,
            )
        ingredients_for_delete.delete()
        instance.tags.clear()
        self.add_data_to_recipe(instance, tags_data, ingredients_data)
        return instance


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe, работающий с полями 'id', 'name',
    'image', 'cooking_time'
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и удаления подписок
    """

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Subscription.objects.filter(
            user=user,
            subscriptions=obj).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        query_params = request.query_params.get('recipes_limit')
        recipes_count = Recipe.objects.filter(author=obj).count()
        if query_params:
            recipes_limit = int(query_params)
        else:
            recipes_limit = recipes_count
        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        serializer = RecipeMinifiedSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        user_id = self.context['view'].kwargs.get('id')
        user = get_object_or_404(User, pk=user_id)
        recipes_count = user.recipes.count()
        return recipes_count


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка подписок
    """

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)
    
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Subscription.objects.filter(
            user=user,
            subscriptions=obj).exists()

    def get_recipes(self, obj):
        request = self.context['request']
        query_params = request.query_params.get('recipes_limit')
        recipes_count = Recipe.objects.filter(author=obj).count()
        if query_params:
            recipes_limit = int(query_params)
        else:
            recipes_limit = recipes_count
        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        serializer = RecipeMinifiedSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        recipes_count = obj.recipes.count()
        return recipes_count

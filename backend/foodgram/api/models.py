from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель для управления ингредиентами
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Возвращает строковое представление модели Ingredient
        """

        return '{}, {}'.format(self.name, self.measurement_unit)


class Tag(models.Model):
    """Модель для управления тэгами
    """

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тэга',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет тэга в HEX',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Уникальный слаг тэга',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        """Возвращает строковое представление модели Tag
        """

        return f'{self.name}'


class Recipe(models.Model):
    """Модель для управления рецептами
    """

    author = models.ForeignKey(
        User,
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
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        """Возвращает строковое представление модели Recipe
        """

        return f'{self.name}'


class IngredientInRecipe(models.Model):
    """Модель для связи рецепта с ингредиентом
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'

        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_name_ingredient_in_recipe',
            )
        ]

    def __str__(self):
        """Возвращает строковое представление модели IngredientInRecipe
        """

        return f'Игредиенты для рецепта "{self.recipe.name}"'


class Subscription(models.Model):
    """Модель для управления подписками
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Пользователь, который подписывается',
    )
    subscriptions = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
        verbose_name='Пользователь, на которого подписываются',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscriptions'],
                name='unique_name_subscriptions',
            )
        ]

    def __str__(self):
        """Возвращает строковое представление модели Subscription
        """

        return f'Подписки пользователя {self.user.username}'


class ShoppingCart(models.Model):
    """Модель для управления списком покупок
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепты, добавленные в список покупок',
    )

    class Meta:
        verbose_name = 'Добавление рецепта в список покупок'
        verbose_name_plural = 'Добавление рецептов в список покупок'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_name_recipe_in_shopping_cart',
            )
        ]

    def __str__(self):
        """Возвращает строковое представление модели ShoppingCart
        """

        return f'Список покупок пользователя {self.user.username}'


class Favorite(models.Model):
    """Модель для добавления рецепта в избранное
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Рецепт, который добавляется в избранное',
    )

    class Meta:
        verbose_name = 'Добавление рецепта в избранное'
        verbose_name_plural = 'Добавление рецептов в избранное'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_name_recipe_in_favorites',
            )
        ]

    def __str__(self):
        """Возвращает строковое представление модели Favorite
        """

        return (f'Рецепты, добавленные в избранное пользователем '
                f'{self.user.username}')

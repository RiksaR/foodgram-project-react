# Generated by Django 4.0.3 on 2022-04-03 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_shoppingcart_user'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_name_user',
        ),
        migrations.RenameField(
            model_name='shoppingcart',
            old_name='recipes',
            new_name='recipe',
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_name_user'),
        ),
    ]
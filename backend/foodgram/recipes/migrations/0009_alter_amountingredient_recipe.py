# Generated by Django 3.2.19 on 2023-05-26 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_shoppingcart_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amountingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='amount_recipe', to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]

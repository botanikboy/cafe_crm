# Generated by Django 4.2 on 2025-02-27 14:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_item_options_alter_itemorder_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ['title'], 'verbose_name': 'Блюдо', 'verbose_name_plural': 'Блюда'},
        ),
        migrations.AlterField(
            model_name='itemorder',
            name='amount',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Итоговая стоимость заказа'),
        ),
        migrations.AlterField(
            model_name='table',
            name='number',
            field=models.SmallIntegerField(unique=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Номер'),
        ),
    ]

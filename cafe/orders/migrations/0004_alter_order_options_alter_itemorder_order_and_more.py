# Generated by Django 4.2 on 2025-02-28 08:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_item_options_alter_itemorder_amount_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['status', 'date_added'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterField(
            model_name='itemorder',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items_in_order', to='orders.order', verbose_name='Заказ'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('1_READY', 'готово'), ('2_PENDING', 'в ожидании'), ('3_PAID', 'оплачено')], default='PENDING', max_length=16, verbose_name='Статус'),
        ),
    ]

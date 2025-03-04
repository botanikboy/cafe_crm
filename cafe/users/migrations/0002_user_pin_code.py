# Generated by Django 4.2 on 2025-03-04 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pin_code',
            field=models.CharField(blank=True, help_text='Используется для входа в систему смен', max_length=4, null=True, unique=True, verbose_name='Пин-код'),
        ),
    ]

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Table(models.Model):
    number = models.SmallIntegerField(
        'Номер',
        unique=True,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'
        ordering = ['number']

    def __str__(self):
        return f'Столик №{self.number}'


class Item(models.Model):
    title = models.CharField(
        'Название',
        max_length=128,
    )
    description = models.TextField(
        'Описание',
        max_length=1024,
        blank=True,
        null=True,
    )
    price = models.DecimalField(
        'Цена',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['title']

    def __str__(self):
        return self.title


class ItemOrder(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Блюдо',
    )
    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='items_in_order',
        verbose_name='Заказ',
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
        default=1,
    )

    class Meta:
        verbose_name = 'Позиция в заказе'
        verbose_name_plural = 'Позиции в заказах'
        ordering = ['order', 'item']

    def __str__(self):
        return f'{self.item.title} x {self.amount}'

    def save(self, *args, **kwargs):
        """Update total_price on change."""
        if self.pk:
            old_amount = ItemOrder.objects.get(pk=self.pk).amount
            difference = (self.amount - old_amount) * self.item.price
            self.order.total_price += difference
        else:
            self.order.total_price += self.amount * self.item.price

        super().save(*args, **kwargs)
        self.order.save(update_fields=['total_price'])

    def delete(self, *args, **kwargs):
        """Update total_price on delete."""
        self.order.total_price -= self.amount * self.item.price
        super().delete(*args, **kwargs)
        self.order.save(update_fields=['total_price'])


class Order(models.Model):
    STATUS_CHOICES = [
        ('1_READY', 'готово'),
        ('2_PENDING', 'в ожидании'),
        ('3_PAID', 'оплачено'),
    ]
    table_number = models.ForeignKey(
        Table,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Стол'
    )
    items = models.ManyToManyField(
        Item,
        through=ItemOrder,
        verbose_name='Блюда в заказе',
    )
    total_price = models.DecimalField(
        'Итоговая стоимость заказа',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        editable=False,
    )
    status = models.CharField(
        'Статус',
        max_length=16,
        choices=STATUS_CHOICES,
        default='2_PENDING',
    )
    date_added = models.DateTimeField(
        'Время создания',
        auto_now_add=True,
        editable=False,
    )
    date_closed = models.DateTimeField(
        'Время закрытия',
        null=True,
        blank=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-status', 'date_added']

    def __str__(self):
        return (
            f"Заказ {self.id} от {self.date_added.isoformat(' ', 'seconds')}"
        )

    def clean_table_number(self):
        """Forbid empty table on creation, but allow null if table deleted."""
        if not self.table_number and not self.pk:
            raise ValidationError(
                {'table_number': 'Выберите стол перед созданием заказа!'}
            )

    def clean(self):
        self.clean_table_number()

    def save(self, *args, **kwargs):
        """Update date_closed when order is paid."""
        self.full_clean()
        if self.status == '3_PAID' and self.date_closed is None:
            self.date_closed = timezone.now()
        elif self.status != '3_PAID':
            self.date_closed = None

        super().save(*args, **kwargs)

    def update_total_price(self):
        total = sum(
            item.item.price * item.amount
            for item in self.items_in_order.all()
        )
        self.total_price = total
        self.save(update_fields=['total_price'])

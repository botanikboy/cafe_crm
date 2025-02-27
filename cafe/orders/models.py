from django.db import models


class Table(models.Model):
    number = models.IntegerField('Номер', unique=True)

    class Meta:
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'
        ordering = ('number',)

    def __str__(self):
        return f'Столик №{self.number}'


class Dish(models.Model):
    title = models.CharField('Название', max_length=128)
    description = models.TextField(
        'Описание', max_length=1024, blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ('id',)

    def __str__(self):
        return self.title


class DishOrder(models.Model):
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name='orders',
        verbose_name='Блюдо'
    )
    order = models.ForeignKey(
        'Order', on_delete=models.CASCADE, related_name='dishes',
        verbose_name='Заказ'
    )
    amount = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Позиция в заказе'
        verbose_name_plural = 'Позиции в заказах'
        ordering = ('order', 'dish')

    def __str__(self):
        return f'{self.amount} × {self.dish.title} (Заказ {self.order.id})'


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'в ожидании'),
        ('READY', 'готово'),
        ('PAID', 'оплачено'),
    ]
    table_number = models.ForeignKey(
        Table, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ManyToManyField(
        Dish, through=DishOrder, verbose_name='Блюда в заказе')
    total_price = models.DecimalField(
        'Итоговая стоимость заказа',
        max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        'Статус', max_length=8, choices=STATUS_CHOICES, default='PENDING')
    date_added = models.DateTimeField('Время создания', auto_now_add=True)
    date_closed = models.DateTimeField('Время закрытия', null=True, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('id', 'status')

    def __str__(self):
        return (
            f"Заказ {self.id} от {self.date_added.isoformat(' ', 'seconds')} "
            f"- {self.get_status_display()}"
        )

    def calculate_total_price(self):
        total = sum(
            item.item.price * item.amount for item in self.dishes.all())
        self.total_price = total
        self.save()

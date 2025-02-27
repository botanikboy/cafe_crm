from django.contrib import admin

from .models import Order, Dish, DishOrder, Table


class DishInline(admin.TabularInline):
    model = DishOrder
    fields = ('dish', 'amount')
    extra = 1
    verbose_name = 'Строка в заказе'
    verbose_name_plural = 'Строки в заказе'


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'table_number', 'total_price',
        'status', 'date_added', 'date_closed',
    )
    search_fields = ('table_number',)
    list_filter = ('table_number', 'status')
    filter_horizontal = ('items',)
    inlines = (DishInline,)


class DishAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'price')
    search_fields = ('title',)


class DishOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'dish', 'order', 'amount')
    search_fields = ('dish', 'order')
    list_filter = ('dish',)


class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'number')
    search_fields = ('number',)


admin.site.register(Order, OrderAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(DishOrder, DishOrderAdmin)

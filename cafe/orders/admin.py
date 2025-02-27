from django.contrib import admin

from .models import Order, Item, ItemOrder, Table


class ItemInline(admin.TabularInline):
    model = ItemOrder
    fields = ('item', 'amount')
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
    inlines = (ItemInline,)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'price')
    search_fields = ('title',)


class ItemOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'order', 'amount')
    search_fields = ('item', 'order')
    list_filter = ('item',)


class TableAdmin(admin.ModelAdmin):
    list_display = ('id', 'number')
    search_fields = ('number',)


admin.site.register(Order, OrderAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(ItemOrder, ItemOrderAdmin)

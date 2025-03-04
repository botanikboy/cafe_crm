from django.contrib import admin
from django.db.models import Sum

from .models import Item, ItemOrder, Shift, Order, Table


class ItemInline(admin.TabularInline):
    model = ItemOrder
    fields = ['item', 'amount', 'get_item_price']
    readonly_fields = ['get_item_price']
    extra = 1
    verbose_name = 'Строка в заказе'
    verbose_name_plural = 'Строки в заказе'

    @admin.display(description='Цена за единицу')
    def get_item_price(self, obj):
        return obj.item.price if obj.item else None


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'table_number', 'total_price', 'shift',
        'status', 'date_added', 'date_closed', 'is_active'
    ]
    search_fields = ['table_number']
    list_filter = ['table_number', 'status', 'is_active']
    filter_horizontal = ['items']
    inlines = [ItemInline]


class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'price', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']


class ItemOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'order', 'amount']
    search_fields = ['item', 'order']
    list_filter = ['item']


class TableAdmin(admin.ModelAdmin):
    list_display = ['id', 'number', 'is_active']
    search_fields = ['number']
    list_filter = ['is_active']


class ShiftAdmin(admin.ModelAdmin):
    list_display = ['id', 'waiter', 'date_added', 'date_closed', 'is_active',
                    'total_revenue']
    search_fields = ['waiter']
    list_filter = ['waiter', 'is_active']
    actions = ['close_selected_shifts']

    @admin.display(description="Выручка за смену")
    def total_revenue(self, obj):
        total = obj.orders.filter(status="3_PAID").aggregate(
            Sum("total_price")
        )["total_price__sum"] or 0
        return f"{total:,.2f} руб".replace(",", " ").replace(".", ",")

    @admin.action(description="Закрыть выбранные смены")
    def close_selected_shifts(self, request, queryset):
        for shift in queryset.filter(is_active=True):
            shift.close_shift()
        self.message_user(request, f"Закрыто смен: {queryset.count()}")


admin.site.register(Order, OrderAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(ItemOrder, ItemOrderAdmin)
admin.site.register(Shift, ShiftAdmin)

from rest_framework import serializers

from orders.models import Order, ItemOrder, Table, Shift
from orders.utils import get_active_shift


class ItemOrderSerializer(serializers.ModelSerializer):
    """Сериализатор для блюд в заказе."""
    item_title = serializers.CharField(source="item.title", read_only=True)

    class Meta:
        model = ItemOrder
        fields = ['id', 'item', 'item_title', 'amount']


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для заказов."""
    items_in_order = ItemOrderSerializer(many=True, read_only=True)
    table_number = serializers.PrimaryKeyRelatedField(
        queryset=Table.objects.filter(is_active=True),
        write_only=True
    )
    shift = serializers.PrimaryKeyRelatedField(
        queryset=Shift.objects.filter(is_active=True),
        required=False
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'table_number',
            'items_in_order',
            'total_price',
            'status',
            'shift',
        ]

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        active_shift = get_active_shift(user)
        if not active_shift:
            raise serializers.ValidationError({"shift": "Нет активной смены."})

        validated_data['shift'] = active_shift

        return super().create(validated_data)

from django.db.models import Q
from django.shortcuts import get_object_or_404
from orders.models import Order
from orders.utils import get_active_shift
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    API для управления заказами.

    Доступные эндпоинты:
    - GET /api/orders/ — список заказов
    - POST /api/orders/ — создание заказа
    - GET /api/orders/{id}/ — получение конкретного заказа
    - PUT /api/orders/{id}/ — полное обновление заказа
    - PATCH /api/orders/{id}/ — частичное обновление заказа
    - DELETE /api/orders/{id}/ — удаление заказа
    - POST /api/orders/{id}/set_status/ — изменение статуса заказа
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Фильтрация заказов только для активной смены или без смены."""

        user = self.request.user
        active_shift = get_active_shift(user)
        return Order.objects.filter(
            Q(shift=active_shift) | Q(shift__isnull=True),
            is_active=True
        )

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        """Изменение статуса заказа через API."""

        order = get_object_or_404(Order, pk=pk, shift__waiter=request.user)

        if not order.shift or not order.shift.is_active:
            return Response(
                {"error": "Смена закрыта, нельзя менять статус заказа"},
                status=400,
            )

        new_status = request.data.get("status")
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"error": "Некорректный статус"}, status=400)

        order.status = new_status
        order.save()
        return Response(
            {"status": (
                f"Заказ {order.id} обновлен до {order.get_status_display()}")}
        )

    def perform_destroy(self, instance):
        """Не удаляет заказ, а делает его неактивным."""
        instance.is_active = False
        instance.save()

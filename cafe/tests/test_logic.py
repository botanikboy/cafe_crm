import pytest
from django.db.models import Sum

from orders.models import Order


@pytest.mark.django_db
def test_create_order(shift, table, item):
    order = Order.objects.create(
        table_number=table,
        shift=shift,
        status='2_PENDING',
        total_price=250.00
    )
    order.items.add(item)
    assert order.table_number == table
    assert order.shift == shift
    assert order.total_price == 250.00
    assert order.status == '2_PENDING'


@pytest.mark.django_db
def test_close_shift(shift, order):
    order.status = '3_PAID'
    order.save()
    shift.close_shift()
    assert not shift.is_active
    assert not Order.objects.filter(id=order.id, is_active=True).exists()


@pytest.mark.django_db
def test_shift_revenue_calculation(shift, order):
    order.status = '3_PAID'
    order.save()
    total_revenue = shift.orders.filter(
        status='3_PAID').aggregate(total=Sum('total_price'))['total'] or 0
    assert total_revenue == 250.00

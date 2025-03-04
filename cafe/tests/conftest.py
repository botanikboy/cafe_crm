import pytest
from django.contrib.auth import get_user_model
from orders.models import Table, Item, Order, Shift
from django.utils import timezone

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='test_user', pin_code='1234')


@pytest.fixture
def another_user(db):
    return User.objects.create_user(username='another_user', pin_code='5678')


@pytest.fixture
def table(db):
    return Table.objects.create(number=1, is_active=True)


@pytest.fixture
def inactive_table(db):
    return Table.objects.create(number=99, is_active=False)


@pytest.fixture
def item(db):
    return Item.objects.create(title='Test Dish', price=250.00, is_active=True)


@pytest.fixture
def shift(db, user):
    return Shift.objects.create(
        waiter=user, date_added=timezone.now(), is_active=True)


@pytest.fixture
def order(db, shift, table, item):
    order = Order.objects.create(
        table_number=table,
        shift=shift, status='2_PENDING',
        total_price=250.00
    )
    order.items.add(item)
    return order

import pytest
from django.test.client import Client
from django.contrib.auth import get_user_model
from orders.models import Table, Item, Shift, Order, ItemOrder
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser', password='testpass', pin_code='1234')


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def table(db):
    return Table.objects.create(number=1, is_active=True)


@pytest.fixture
def item(db):
    return Item.objects.create(title='Пицца', price=250.50, is_active=True)


@pytest.fixture
def shift(db, user):
    return Shift.objects.create(waiter=user, is_active=True)


@pytest.fixture
def order(db, shift, table):
    return Order.objects.create(
        table_number=table, shift=shift, status='2_PENDING',
        total_price=0, is_active=True
    )


@pytest.fixture
def item_order(db, order, item):
    return ItemOrder.objects.create(order=order, item=item, amount=2)


@pytest.fixture
def create_shift(user):
    return Shift.objects.create(waiter=user, is_active=True)


@pytest.fixture
def create_table():
    return Table.objects.create(number=2, is_active=True)


@pytest.fixture
def create_item():
    return Item.objects.create(title='Суши', price=500.00, is_active=True)


@pytest.fixture
def create_order(create_shift, create_table):
    order = Order.objects.create(
        table_number=create_table, shift=create_shift, status='2_PENDING',
        total_price=0, is_active=True
    )
    return order

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_orders_list_content(client, user, shift, order):
    client.force_login(user)
    response = client.get(reverse('orders:orders_list'))
    assert response.status_code == 200
    assert str(order.id).encode() in response.content
    assert order.table_number.__str__().encode() in response.content


@pytest.mark.django_db
def test_order_detail_content(client, user, order):
    client.force_login(user)
    response = client.get(reverse('orders:order_edit', args=[order.id]))
    assert response.status_code == 200
    assert 'Редактирование заказа'.encode("utf-8") in response.content
    assert str(order.total_price).encode() in response.content

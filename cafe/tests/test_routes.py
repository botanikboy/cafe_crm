import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_index_view(client):
    response = client.get(reverse('orders:index'))
    assert response.status_code == 200
    assert 'Открытие смены'.encode("utf-8") in response.content


@pytest.mark.django_db
def test_orders_list_view(client, user, shift):
    client.force_login(user)
    response = client.get(reverse('orders:orders_list'))
    assert response.status_code == 200
    assert 'Список заказов за смену'.encode("utf-8") in response.content


@pytest.mark.django_db
def test_order_create_view(client, user, shift):
    client.force_login(user)
    response = client.get(reverse('orders:order_create'))
    assert response.status_code == 200
    assert 'Новый заказ'.encode("utf-8") in response.content


@pytest.mark.django_db
def test_order_update_view(client, user, order):
    client.force_login(user)
    response = client.get(reverse('orders:order_edit', args=[order.id]))
    assert response.status_code == 200
    assert 'Редактирование заказа'.encode("utf-8") in response.content


@pytest.mark.django_db
def test_order_delete_view(client, user, order):
    client.force_login(user)
    response = client.get(reverse('orders:order_delete', args=[order.id]))
    assert response.status_code == 200
    assert 'Удаление заказа'.encode("utf-8") in response.content

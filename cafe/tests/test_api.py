import pytest
from django.urls import reverse
from rest_framework import status
from orders.models import Order


@pytest.mark.django_db
def test_get_orders(auth_client, create_order):
    """Тест получения списка заказов"""
    url = reverse('api:order-list')
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['id'] == create_order.id


@pytest.mark.django_db
def test_create_order(auth_client, create_shift, create_table, create_item):
    payload = {
        "table_number": create_table.id,
        "shift": create_shift.id,
        "items_in_order": [{"item": create_item.id, "amount": 1}],
        "status": "2_PENDING"
    }
    response = auth_client.post(
        reverse("api:order-list"), payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Order.objects.count() > 0


@pytest.mark.django_db
def test_update_order_status(auth_client, create_order):
    """Тест обновления статуса заказа"""
    url = reverse('api:order-detail', args=[create_order.id])
    data = {"status": "3_PAID"}
    response = auth_client.patch(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    create_order.refresh_from_db()
    assert create_order.status == "3_PAID"


@pytest.mark.django_db
def test_delete_order(auth_client, create_order):
    """Тест на удаление заказа (устанавливает is_active=False)."""
    url = reverse('api:order-detail', args=[create_order.id])
    response = auth_client.delete(url)
    create_order.refresh_from_db()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not create_order.is_active

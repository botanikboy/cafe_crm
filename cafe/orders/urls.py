from django.urls import path

from .views import (OrderCreate, OrderDelete, OrderList, OrderUpdate,
                    open_shift, close_shift)

app_name = 'orders'

urlpatterns = [
    path('', open_shift, name='index'),
    path('orders/', OrderList.as_view(), name='orders_list'),
    path('orders/create', OrderCreate.as_view(), name='order_create'),
    path('orders/edit/<int:pk>', OrderUpdate.as_view(), name='order_edit'),
    path('orders/delete/<int:pk>', OrderDelete.as_view(), name='order_delete'),
    path('close-shift/', close_shift, name='close_shift')
]

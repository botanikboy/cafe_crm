from django.urls import path

from .views import Help, OrderCreate, OrderDelete, OrderList, OrderUpdate

app_name = 'orders'

urlpatterns = [
    path('', OrderList.as_view(), name='index'),
    path('orders/', OrderList.as_view(), name='orders_list'),
    path('orders/create', OrderCreate.as_view(), name='order_create'),
    path('orders/edit/<int:pk>', OrderUpdate.as_view(), name='order_edit'),
    path('orders/delete/<int:pk>', OrderDelete.as_view(), name='order_delete'),
    path('help/', Help.as_view(), name='help')
]

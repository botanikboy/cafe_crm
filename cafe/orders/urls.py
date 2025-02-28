from django.urls import path

from .views import OrderListView, Help

app_name = 'orders'

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='orders_list'),
    path('help/', Help.as_view(), name='help')
]

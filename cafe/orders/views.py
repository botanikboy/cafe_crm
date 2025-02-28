from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, ListView,
                                  TemplateView, UpdateView)

from .models import ItemOrder, Order


class OrderList(ListView):
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.all().prefetch_related(
            Prefetch(
                'items_in_order',
                queryset=ItemOrder.objects.select_related('item')
            )
        ).select_related('table_number').order_by('status', 'date_added')


class Help(TemplateView):
    template_name = 'orders/help.html'


class OrderCreate(CreateView):
    model = Order
    fields = ['table_number', 'items']
    success_url = reverse_lazy('orders:orders_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.update_total_price()
        return response


class OrderUpdate(UpdateView):
    model = Order
    fields = ['table_number', 'items', 'status']
    success_url = reverse_lazy('orders:orders_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.update_total_price()
        return response


class OrderDelete(DeleteView):
    model = Order
    success_url = reverse_lazy('orders:orders_list')
    template_name = 'orders/order_form.html'

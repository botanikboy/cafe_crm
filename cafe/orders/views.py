from django.db.models import Prefetch
from django.views.generic import ListView, TemplateView

from .models import Order, ItemOrder


class OrderListView(ListView):
    queryset = Order.objects.all().prefetch_related(
        Prefetch(
            'items_in_order',
            queryset=ItemOrder.objects.select_related(
                'item'
            )
        )
    ).select_related('table_number')
    ordering = ['status', 'date_added']
    paginate_by = 10


class Help(TemplateView):
    template_name = 'orders/help.html'

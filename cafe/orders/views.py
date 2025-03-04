from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, ListView,
                                  TemplateView, UpdateView)
from django.shortcuts import redirect

from .forms import ItemOrderFormSet
from .models import ItemOrder, Order


class OrderList(ListView):
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.all().prefetch_related(
            Prefetch(
                'items_in_order',
                queryset=ItemOrder.objects.select_related('item')
            )
        ).select_related('table_number').order_by('status', 'date_added')

        status_filter = self.request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        table_filter = self.request.GET.get("table")
        if table_filter:
            queryset = queryset.filter(
                table_number__number__icontains=table_filter)

        return queryset


class Help(TemplateView):
    template_name = 'orders/help.html'


class OrderMixing:
    model = Order
    success_url = reverse_lazy('orders:orders_list')


class OrderFormsetMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = getattr(self, 'object', None)

        if self.request.method == 'POST':
            context['formset'] = ItemOrderFormSet(
                self.request.POST,
                instance=order,
                prefix='form',
            )
        else:
            context['formset'] = ItemOrderFormSet(
                instance=order,
                prefix='form',
            )

        return context

    def form_valid(self, form):
        formset = ItemOrderFormSet(
            self.request.POST,
            instance=self.object,
            prefix='form',
        )

        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            order.update_total_price()
            return redirect(self.success_url)

        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class OrderCreate(OrderMixing, OrderFormsetMixin, CreateView):
    fields = ['table_number']


class OrderUpdate(OrderMixing, OrderFormsetMixin, UpdateView):
    fields = ['status']


class OrderDelete(OrderMixing, DeleteView):
    template_name = 'orders/confirm_delete_order.html'

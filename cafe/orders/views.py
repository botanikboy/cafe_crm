from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, ListView,
                                  TemplateView, UpdateView)
from django.shortcuts import redirect

from .models import ItemOrder, Order
from .forms import ItemOrderFormSet


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
    fields = ['table_number']
    success_url = reverse_lazy('orders:orders_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['formset'] = ItemOrderFormSet(
                self.request.POST,
                prefix='form'
            )
        else:
            context['formset'] = ItemOrderFormSet(
                prefix='form'
            )
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = ItemOrderFormSet(
            self.request.POST,
            prefix='form'
        )
        if form.is_valid() and formset.is_valid():
            return self.form_and_formset_valid(form, formset)
        else:
            return self.form_and_formset_invalid(form, formset)

    def form_and_formset_valid(self, form, formset):
        self.object = form.save(commit=False)
        self.object.save()
        formset.instance = self.object
        formset.save()
        self.object.update_total_price()
        return redirect(self.success_url)

    def form_and_formset_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


class OrderUpdate(UpdateView):
    model = Order
    fields = ['status']
    success_url = reverse_lazy('orders:orders_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object

        if self.request.method == 'POST':
            context['formset'] = ItemOrderFormSet(
                self.request.POST, instance=order, prefix='form')
        else:
            context['formset'] = ItemOrderFormSet(
                instance=order, prefix='form')

        return context

    def form_valid(self, form):
        formset = ItemOrderFormSet(
            self.request.POST, instance=self.object, prefix='form')

        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            order.update_total_price()
            return redirect(self.success_url)

        return self.form_invalid(form)


class OrderDelete(DeleteView):
    model = Order
    success_url = reverse_lazy('orders:orders_list')
    template_name = 'orders/confirm_delete_order.html'

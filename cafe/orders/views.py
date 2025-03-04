from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Sum, Q
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, ListView,
                                  UpdateView)

from .forms import ItemOrderFormSet
from .models import ItemOrder, Order, Shift

User = get_user_model()


class OrderList(ListView, LoginRequiredMixin):
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        active_shift = Shift.objects.filter(
            waiter=user, is_active=True).first()
        queryset = Order.objects.filter(is_active=True).filter(
            Q(shift=active_shift) | Q(shift__isnull=True)
        ).prefetch_related(
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


class OrderMixing(LoginRequiredMixin):
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

    def assign_shift(self, order, form):
        if not order.shift:
            active_shift = Shift.objects.filter(
                waiter=self.request.user, is_active=True).first()
            if not active_shift:
                form.add_error(None, "У вас нет открытой смены!")
                return False
            order.shift = active_shift
        return True

    def form_valid(self, form):
        formset = ItemOrderFormSet(
            self.request.POST,
            instance=self.object,
            prefix='form',
        )

        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            if not self.assign_shift(order, form):
                return self.form_invalid(form)
            order.save()
            formset.instance = order
            formset.save()
            order.update_total_price()
            return redirect(self.success_url)

        return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class OrderCreate(OrderMixing, OrderFormsetMixin, CreateView):
    fields = ['table_number']


class OrderPermissionMixin:
    def dispatch(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        active_shift = Shift.objects.filter(
            waiter=request.user, is_active=True).first()

        if not order.is_active or (
                order.shift and order.shift != active_shift):
            raise PermissionDenied("Вы не можете изменить этот заказ!")

        return super().dispatch(request, *args, **kwargs)


class OrderUpdate(
        OrderPermissionMixin, OrderMixing, OrderFormsetMixin, UpdateView):
    fields = ['status']


class OrderDelete(OrderPermissionMixin, OrderMixing, DeleteView):
    template_name = 'orders/confirm_delete_order.html'


def open_shift(request):
    if request.method == "POST":
        pin_code = request.POST.get("pin_code")
        user = User.objects.filter(pin_code=pin_code).first()

        if user:
            login(request, user)
            shift, created = Shift.objects.get_or_create(
                waiter=user, is_active=True)
            return redirect("orders:orders_list")
        else:
            return render(
                request, "index.html", {"error": "Неверный пин-код!"})

    return render(request, "orders/index.html")


@login_required
def close_shift(request):
    user = request.user
    shift = get_object_or_404(Shift, waiter=user, is_active=True)
    paid_orders = shift.orders.filter(status='3_PAID', is_active=True)
    total_revenue = paid_orders.aggregate(
        Sum('total_price'))['total_price__sum'] or 0
    total_revenue_display = f"{total_revenue:,.2f} руб".replace(
        ",", " ").replace(".", ",")
    if request.method == "POST":
        shift.close_shift()
        return redirect('orders:index')

    context = {
        'page_obj': paid_orders,
        'total_revenue': total_revenue_display,
    }

    return render(request, "orders/order_list.html", context)

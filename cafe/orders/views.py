from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Q, Sum
from django.shortcuts import redirect, render
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import OrderCreateForm, OrderUpdateForm
from .mixins import (ActiveShiftMixin, OrderFormsetMixin, OrderMixing,
                     OrderPermissionMixin)
from .models import ItemOrder, Order, Shift
from .utils import get_active_shift

User = get_user_model()


class OrderList(LoginRequiredMixin, ActiveShiftMixin, ListView):
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


class OrderCreate(
    OrderMixing, OrderFormsetMixin, ActiveShiftMixin, CreateView
        ):
    form_class = OrderCreateForm


class OrderUpdate(
        OrderPermissionMixin, OrderMixing, OrderFormsetMixin, ActiveShiftMixin,
        UpdateView
        ):
    form_class = OrderUpdateForm


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
                request, "orders/index.html", {"error": "Неверный пин-код!"})

    return render(request, "orders/index.html")


@login_required
def close_shift(request):
    user = request.user
    shift = get_active_shift(user)
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
        'shift': shift,
    }

    return render(request, "orders/order_list.html", context)

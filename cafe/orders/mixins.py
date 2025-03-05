from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from .forms import ItemOrderFormSet
from .models import Order, Shift
from .utils import get_active_shift


class OrderMixing(LoginRequiredMixin):
    model = Order
    success_url = reverse_lazy('orders:orders_list')


class OrderFormsetMixin:
    '''
    Миксин для обработки создания и редактирования заказов (Order).
    Добавляет в контекст:
        - `formset` (ItemOrderFormSet): формсет для работы с блюдами в заказе.

    Методы:
        - get_context_data: добавляет в контекст формсет.
        - assign_shift: привязывает заказ к активной смене пользователя.
        - form_valid: сохраняет заказ и обновляет его стоимость.
        - form_invalid: возвращает форму с ошибками валидации.

    Используется в:
        - OrderCreate
        - OrderUpdate
    '''

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


class OrderPermissionMixin:
    '''Миксин для запрета редактирвоания чужих и неактивных заказов.'''

    def dispatch(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=self.kwargs["pk"])
        active_shift = Shift.objects.filter(
            waiter=request.user, is_active=True).first()

        if not order.is_active or (
                order.shift and order.shift != active_shift):
            raise PermissionDenied("Вы не можете изменить этот заказ!")

        return super().dispatch(request, *args, **kwargs)


class ActiveShiftMixin:
    '''Миксин для добавления активной смены в контекст.'''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shift'] = get_active_shift(self.request.user) or None
        return context

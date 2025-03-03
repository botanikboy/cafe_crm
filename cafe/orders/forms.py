from django import forms
from django.forms import inlineformset_factory
from .models import Order, ItemOrder


class ItemOrderForm(forms.ModelForm):
    class Meta:
        model = ItemOrder
        fields = ['item', 'amount']


ItemOrderFormSet = inlineformset_factory(
    Order, ItemOrder, form=ItemOrderForm,
    extra=1, can_delete=True
)

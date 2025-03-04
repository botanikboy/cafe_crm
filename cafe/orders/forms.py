from django import forms
from django.forms import inlineformset_factory
from .models import Order, ItemOrder


class ItemOrderForm(forms.ModelForm):
    class Meta:
        model = ItemOrder
        fields = ['item', 'amount']

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        if not item:
            self._errors.pop('amount', None)
        return cleaned_data


ItemOrderFormSet = inlineformset_factory(
    Order, ItemOrder, form=ItemOrderForm,
    extra=1, can_delete=True
)

from django import forms
from django.forms import inlineformset_factory

from .models import Item, ItemOrder, Order


class ItemOrderForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        empty_label="Выберите блюдо",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

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

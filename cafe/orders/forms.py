from django import forms
from django.forms import inlineformset_factory

from .models import Item, ItemOrder, Order, Table


class ItemOrderForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=Item.objects.filter(is_active=True),
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


class OrderCreateForm(forms.ModelForm):
    table_number = forms.ModelChoiceField(
        queryset=Table.objects.filter(is_active=True),
        empty_label="Выберите стол",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Order
        fields = ['table_number']

    def clean_table_number(self):
        table = self.cleaned_data.get('table_number')
        if table and not table.is_active:
            raise forms.ValidationError("Выбранный стол больше не доступен!")
        return table


class OrderUpdateForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=Order.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Order
        fields = ['table_number', 'status']

    def clean_item(self):
        item = self.cleaned_data.get('item')
        if item and not item.is_active:
            raise forms.ValidationError("Выбранное блюдо больше не доступно!")
        return item

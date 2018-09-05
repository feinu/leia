from django import forms

from .models import Client, Product


class LineItemForm(forms.Form):
    product = forms.ModelChoiceField(label='Product',
                                     queryset=Product.objects.all())
    quantity = forms.DecimalField(label='Quantity', initial=1, min_value=0,
                                  max_digits=5, decimal_places=2)


class InvoiceForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(),
                                    widget=forms.HiddenInput)


class PaymentForm(forms.Form):
    client = forms.ModelChoiceField(queryset=Client.objects.all(),
                                    widget=forms.HiddenInput)
    amount = forms.DecimalField(label='Amount', initial=0, min_value=0.01,
                                max_digits=5, decimal_places=2)
    date = forms.DateField(label='Date')

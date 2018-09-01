from django import forms

from .models import Product

class LineItemForm(forms.Form):
    product = forms.ModelChoiceField(label='Product',
                                     queryset=Product.objects.all())
    quantity = forms.DecimalField(label='Quantity', initial=1, min_value=0,
                                  max_digits=5, decimal_places=2)

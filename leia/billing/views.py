from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, FormView

from .models import Client, Product, LineItem
from .forms import LineItemForm


class ClientCreate(CreateView):
    model = Client
    fields = ['name', 'email']


class ProductCreate(CreateView):
    model = Product
    fields = ['name', 'unit_price']
    success_url = reverse_lazy('productlist')


class ProductList(ListView):
    model = Product


class LineItemCreate(CreateView):
    model = LineItem
    fields = ['product', 'quantity', 'date', 'client']


class ClientDetails(DetailView, FormView):
    model = Client
    form_class = LineItemForm

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        outstanding = [
            {
                'date': item.date,
                'description': item.product.name,
                'quantity': item.quantity,
                'amount': item.amount
            }
            for item in LineItem.objects.filter(client=self.get_object(),
                                                invoice=None)
        ]

        context['balance'] = '0.00'
        context['outstanding_amount'] = sum([x['amount'] for x in outstanding])
        context['outstanding_items'] = outstanding
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        product = data['product']
        print(product)
        quantity = data['quantity']
        print(self.__dict__)
        line_item = LineItem(
            client=self.get_object(),
            product=product,
            quantity=quantity,
            amount=product.unit_price * quantity
        )
        line_item.save()
        return super().form_valid(form)



# class NewCharge(FormView):
#     form_class = None

from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, RedirectView
from django.views.generic.edit import CreateView, FormView

from .models import Client, Product, LineItem, Payment
from .forms import InvoiceForm, LineItemForm, PaymentForm


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
        payments = [
            {
                'date': payment.date,
                'amount': payment.amount,
            }
            for payment in Payment.objects.filter(client=self.get_object())
        ]

        context['balance'] = '0.00'
        context['outstanding_amount'] = sum([x['amount'] for x in outstanding])
        context['outstanding_items'] = outstanding
        context['payments'] = payments
        context['invoice_form'] = kwargs.get('invoiceform') or InvoiceForm(
            initial={'client': self.object.pk})
        context['payment_form'] = kwargs.get('paymentform') or PaymentForm(
            initial={
                'date': timezone.now(),
                'client': self.object,
            })
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


class PaymentCreate(FormView):
    form_class = PaymentForm
    template_name = 'billing/payment_create.html'

    def post(self, request):
        print('post')
        print(request.__dict__)
        return super().post(self, request)

    def get_success_url(self):
        print('succesurl')
        return self.object.client.get_absolute_url()

    def form_valid(self, form):
        print('form_valid')
        amount = form.cleaned_data['amount']
        date = form.cleaned_data['date']
        self.object = form.cleaned_data['client'].new_payment(amount, date)
        return super().form_valid(form)


class InvoiceCreate(FormView):
    form_class = InvoiceForm

    def get_success_url(self):
        return self.object.client.get_absolute_url()

    def form_valid(self, form):
        self.object = form.cleaned_data['client'].new_invoice()
        return super().form_valid(form)

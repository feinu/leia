from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone


class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def get_absolute_url(self):
        return reverse_lazy('clientview', args=(self.pk,))

    def new_invoice(self):
        invoice = Invoice(client=self)
        invoice.save()
        for line_item in LineItem.objects.filter(client=self, invoice=None):
            line_item.invoice = invoice
            line_item.save
        return invoice

    def balance(self, date=timezone.now()):
        return (
            sum([x.amount for x in LineItem.objects.filter(date__lte=date)]) -
            sum([x.amount for x in Payment.objects.filter(date__lte=date)])
        )


class Product(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    def dict(self):
        data = dict()
        data['client'] = {
            'name': self.client.name,
        }
        data['lineitems'] = [x.dict() for x in self.lineitem_set.all()]
        data['balance'] = {
            'opening': 0,  # TODO ordering for invoices to get previous one
            'closing': self.client.balance()
        }

        return data


class LineItem(models.Model):
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, null=True, default=None,
                                on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def dict(self):
        return {
            'quantity': self.quantity,
            'description': self.product.name,
            'date': self.date,
            'amount': self.amount
        }


class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(default=timezone.now)

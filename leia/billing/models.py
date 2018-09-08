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
        line_items = LineItem.objects.filter(client=self, invoice=None)
        if len(line_items) == 0:
            return None
        for line_item in line_items:
            line_item.invoice = invoice
            line_item.save()
        return invoice

    def new_payment(self, amount, date=None):
        payment = Payment(client=self, amount=amount, date=date)
        payment.save()
        return payment

    def __str__(self):
        return self.name

    def balance(self, date=timezone.now()):
        return (
            sum([x.amount for x in LineItem.objects.filter(date__lte=date)]) -
            sum([x.amount for x in Payment.objects.filter(date__lte=date)])
        )


class Product(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        get_latest_by = 'date'

    def get_absolute_url(self):
        return reverse_lazy('invoiceview', args=(self.pk,))

    def previous_invoice(self):
        return Invoice.objects.filter(
            client=self.client,
            date__lt=self.date
        ).latest()

    def previous_date(self):
        try:
            return self.previous_invoice().date
        except Invoice.DoesNotExist:
            return timezone.datetime(1970, 1, 1, 0, 0)

    def dict(self):
        data = dict()
        data['pk'] = self.pk
        data['client'] = {
            'name': self.client.name,
        }
        charges = [x.dict() for x in self.lineitem_set.all()]
        payments = [
            x.lineitem() for x in Payment.objects.filter(
                date__gt=self.previous_date(),
                date__lte=self.date
            )
        ]
        data['lineitems'] = sorted(charges + payments, key=lambda x: x['date'])
        data['balance'] = {
            'opening': self.client.balance(self.previous_date()),
            'closing': self.client.balance()
        }
        data['url'] = {
            'view': self.get_absolute_url(),
            'download': None
        }

        return data

    def __str__(self):
        return ' '.join([self.client.name, self.date.strftime('%Y-%m-%d')])


class LineItem(models.Model):
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, null=True, default=None,
                                on_delete=models.SET_NULL)
    date = models.DateTimeField(default=timezone.now)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return ' '.join([self.product.name, str(self.quantity)])

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
    date = models.DateTimeField(default=timezone.now)

    def lineitem(self):
        return {
            'date': self.date,
            'amount': - self.amount,
            'quantity': '',
            'description': 'Payment'
        }

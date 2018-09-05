from django.urls import path

from .views import (ClientCreate, ClientDetails, InvoiceCreate, ProductCreate,
                    LineItemCreate, PaymentCreate, ProductList)

urlpatterns = [
    path('client/create/', ClientCreate.as_view(), name='clientcreate'),
    path('client/<pk>/', ClientDetails.as_view(), name='clientview'),
    path('product/create/', ProductCreate.as_view(), name='productcreate'),
    path('product/list/', ProductList.as_view(), name='productlist'),
    path('lineitem/create/', LineItemCreate.as_view(), name='lineitemcreate'),
    path('invoice/create/', InvoiceCreate.as_view(), name='invoicecreate'),
    path('payment/create/', PaymentCreate.as_view(), name='paymentcreate'),
]

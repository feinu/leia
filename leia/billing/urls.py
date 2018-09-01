from django.urls import path

from .views import (ClientCreate, ClientDetails, ProductCreate,
                    LineItemCreate, ProductList)

urlpatterns = [
    path('client/create/', ClientCreate.as_view(), name='clientcreate'),
    path('client/<pk>/', ClientDetails.as_view(), name='clientview'),
    path('product/create/', ProductCreate.as_view(), name='productcreate'),
    path('product/list/', ProductList.as_view(), name='productlist'),
    path('lineitem/create/', LineItemCreate.as_view(), name='lineitemcreate'),
]

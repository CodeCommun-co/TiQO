from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index.as_view(), name='index'),
    path('create_odoo_contact/<uuid:uuid>', views.create_odoo_contact.as_view(), name='create_odoo_contact'),
]

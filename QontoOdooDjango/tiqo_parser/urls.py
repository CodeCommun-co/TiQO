from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index.as_view(), name='index'),
    path('material', material.as_view(), name='index'),
    path('create_odoo_contact/<uuid:uuid>', create_odoo_contact.as_view(), name='create_odoo_contact'),
    path('action/refresh_qonto_label', refresh_qonto_label.as_view(), name='refresh_qonto_label'),
    path('action/refresh_qonto_transactions', refresh_qonto_transactions.as_view(), name='refresh_qonto_transactions'),
    path('action/refresh_qonto_contacts', refresh_qonto_contacts.as_view(), name='refresh_qonto_contacts'),
    path('action/refresh_odoo_contacts', refresh_odoo_contacts.as_view(), name='refresh_odoo_contacts'),
    path('action/refresh_odoo_articles', refresh_odoo_articles.as_view(), name='refresh_odoo_articles'),
    path('action/refresh_analytic_account', refresh_analytic_account.as_view(), name='refresh_analytic_account'),
    path('action/refresh_journal_account', refresh_journal_account.as_view(), name='refresh_journal_account'),
    path('action/refresh_account_account', refresh_account_account.as_view(), name='refresh_account_account'),

]

from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.views import View
from tiqo_parser.models import Configuration, Label, AccountJournal, AccountAnalyticAccount, Transaction, OdooContact, \
    QontoContact, AccountAccount
import requests
import re, uuid
from django.contrib import messages
from tiqo_parser.odoo_api import OdooApi
from tiqo_parser.qonto_api import QontoApi
from django.contrib.auth.decorators import login_required
# from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from tiqo_parser.serializers import LabelsSerializer, TransactionsSerializer

import logging

logger = logging.getLogger(__name__)


# Fonction qui trouve si une uuid est dans une string :
def find_uuid_in_string(string):
    uuid_regex = re.compile('[a-f\d]{4}(?:[a-f\d]{4}-){4}[a-f\d]{12}')
    find = uuid_regex.findall(string)
    if find:
        return uuid.UUID(find[0])
    return None


class refresh_odoo_articles(View):

    @method_decorator(login_required)
    def get(self, request):
        odooApi = OdooApi()
        articles = odooApi.get_all_articles()
        messages.success(request, f"Articles mis à jour. Total : {articles.count()}")
        return redirect('/admin/tiqo_parser/label')


class refresh_qonto_label(View):

    @method_decorator(login_required)
    def get(self, request):
        qontoApi = QontoApi()
        labels = qontoApi.get_all_labels()
        messages.success(request, f"labels mis à jour. Total : {len(Label.objects.all())}")
        return redirect('/admin/tiqo_parser/label')


class refresh_qonto_transactions(View):

    @method_decorator(login_required)
    def get(self, request):
        qontoApi = QontoApi()
        qontoApi.get_all_transactions()
        messages.success(request, f"Transactions mises à jour. Total : {len(Transaction.objects.all())}")

        return redirect('/admin/tiqo_parser/transaction')


class refresh_odoo_contacts(View):

    @method_decorator(login_required)
    def get(self, request):
        odooApi = OdooApi()
        odooApi.get_all_contacts()
        messages.success(request, f"Contacts mis à jour. Total : {len(OdooContact.objects.all())}")
        return redirect('/admin/tiqo_parser/qontocontact')


class refresh_qonto_contacts(View):

    @method_decorator(login_required)
    def get(self, request):
        qontoApi = QontoApi()
        qontoApi.get_all_contacts()
        messages.success(request, f"Contacts mis à jour. Total : {len(QontoContact.objects.all())}")
        return redirect('/admin/tiqo_parser/qontocontact')

class refresh_account_account(View):

        @method_decorator(login_required)
        def get(self, request):
            odooApi = OdooApi()
            odooApi.get_account_account()
            messages.success(request,
                            f"Comptes de tiers Odoo mis à jour. Total : {len(AccountAccount.objects.all())}")
            return redirect('/admin/tiqo_parser/label')

class refresh_journal_account(View):

    @method_decorator(login_required)
    def get(self, request):
        odooApi = OdooApi()
        odooApi.get_account_journal()
        messages.success(request,
                         f"Journaux de compte Odoo mis à jour. Total : {len(AccountJournal.objects.all())}")
        return redirect('/admin/tiqo_parser/label')

class refresh_analytic_account(View):

    @method_decorator(login_required)
    def get(self, request):
        odooApi = OdooApi()
        odooApi.get_account_analytic()
        messages.success(request,
                         f"Comptes analytiques mis à jour. Total : {len(AccountAnalyticAccount.objects.all())}")
        return redirect('/admin/tiqo_parser/label')


class create_odoo_contact(View):

    @method_decorator(login_required)
    def get(self, request, uuid):
        qonto_contact = QontoContact.objects.get(uuid=uuid)

        email = qonto_contact.email
        name = f"{qonto_contact}"

        if not email:
            messages.add_message(request, messages.ERROR, 'Pas d\'email pour ce contact Qonto')
            email = f"{slugify(name)}@{slugify(name)}.com"
        if not qonto_contact.odoo_contact:
            odooApi = OdooApi()
            response_odoo = odooApi.gc_contact(email, name)
            if response_odoo.get('result'):
                all_odoo_contacts = odooApi.get_all_contacts()
                odoo_contact = all_odoo_contacts.get(email=email)
                qonto_contact.email = email
                qonto_contact.odoo_contact = odoo_contact
                qonto_contact.save()

        return redirect('index')


class index(View):

    @method_decorator(login_required)
    def get(self, request):
        labels = LabelsSerializer(Label.objects.all())
        account_journal = AccountJournal.objects.all()
        account_analytic = AccountAnalyticAccount.objects.all().order_by('group__name')
        alltransactions = TransactionsSerializer(Transaction.objects.all())
        odoo_contacts = OdooContact.objects.all()
        qonto_contacts = QontoContact.objects.all()

        # messages.add_message(request, messages.INFO, 'Hello world.')

        context = {
            "labels": labels,
            "account_journal": account_journal,
            "account_analytic": account_analytic,
            "alltransactions": alltransactions,
            "odoo_contacts": odoo_contacts,
            "qonto_contacts": qonto_contacts,
        }
        return render(request, 'index.html', context=context)


class material(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'material.html')

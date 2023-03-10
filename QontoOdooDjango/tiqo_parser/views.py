from django.shortcuts import render, redirect
from django.views import View
from tiqo_parser.models import Configuration, Label, AccountJournal, AccountAnalyticAccount, Transaction
import requests
import re, uuid

from tiqo_parser.odoo_api import OdooApi
from tiqo_parser.qonto_api import QontoApi

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


# Technique de sioux qui me permet de ne pas faire une class par bouton ...
# En gros, si le formulaire renvoie un inpoute avec name="button_action" value="get_labels"
# alors je lance la fonction get_labels() de la class QontoApi
def button_action_qonto(action):
    QONTO_ACTIONS_POSSIBLE = [
        "get_labels",
        "get_transactions",
    ]
    logger.info(f"button_action_qonto : {action}")
    if action in QONTO_ACTIONS_POSSIBLE:
        qontoApi = QontoApi()
        return getattr(qontoApi, action)()


def button_action_odoo(action):
    ODOO_ACTIONS_POSSIBLE = [
        "get_account_journal",
        "get_account_analytic",
    ]
    logger.info(f"button_action_odoo : {action}")
    if action in ODOO_ACTIONS_POSSIBLE:
        odooApi = OdooApi()
        return getattr(odooApi, action)()


def label_to_account_analytic(label_uuid, account_uuid):
    label_child_uuid = find_uuid_in_string(label_uuid)
    odoo_account_uuid = find_uuid_in_string(account_uuid)
    if label_child_uuid and odoo_account_uuid:
        label = Label.objects.get(uuid=label_child_uuid)
        odoo_account = AccountAnalyticAccount.objects.get(uuid=odoo_account_uuid)
        label.odoo_analytic_account = odoo_account
        label.save()
        print(f"Label {label} lié à {odoo_account}")


class index(View):

    def get(self, request):
        labels = LabelsSerializer(Label.objects.all())
        account_journal = AccountJournal.objects.all()
        account_analytic = AccountAnalyticAccount.objects.all().order_by('group__name')
        alltransactions = TransactionsSerializer(Transaction.objects.all())

        context = {
            "labels": labels,
            "account_journal": account_journal,
            "account_analytic": account_analytic,
            "alltransactions": alltransactions,
            "message": "Hello, world.",
        }
        return render(request, 'index.html', context=context)

    def post(self, request):
        data = request.POST
        print(f'POST INDEX data : {data}')

        # Bouton action pour get Odoo et get Qonto
        for input, value in data.items():
            if input == "button_action_qonto":
                result = button_action_qonto(value)
                print(f'result {result}')
            elif input == "button_action_odoo":
                result = button_action_odoo(value)
                print(f'result {result}')
            elif "odoo_account_select_" in input:
                label_to_account_analytic(input, value)

        return redirect('index')

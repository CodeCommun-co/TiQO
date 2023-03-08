from django.shortcuts import render, redirect
from django.views import View
from tiqo_parser.models import Configuration, Label, AccountJournal
import requests

from tiqo_parser.odoo_api import OdooApi
from tiqo_parser.qonto_api import QontoApi

from tiqo_parser.serializers import LabelsSerializer

import logging

logger = logging.getLogger(__name__)



# Technique de sioux qui me permet de ne pas faire une class par bouton ...
# En gros, si le formulaire renvoie un inpoute avec name="button_action" value="get_labels"
# alors je lance la fonction get_labels() de la class QontoApi
def button_action_qonto(action):
    QONTO_ACTIONS_POSSIBLE = [
        "get_labels",
    ]
    logger.info(f"button_action_qonto : {action}")
    if action in QONTO_ACTIONS_POSSIBLE:
        qontoApi = QontoApi()
        return getattr(qontoApi, action)()

def button_action_odoo(action):
    ODOO_ACTIONS_POSSIBLE = [
        "get_account_journal",
    ]
    logger.info(f"button_action_odoo : {action}")
    if action in ODOO_ACTIONS_POSSIBLE:
        odooApi = OdooApi()
        return getattr(odooApi, action)()


class index(View):

    def get(self, request):
        labels = LabelsSerializer(Label.objects.all())
        account_journal = AccountJournal.objects.all()

        context = {
            "labels" : labels,
            "account_journal" : account_journal,
            "message": "Hello, world.",
        }
        return render(request, 'index.html', context=context)

    def post(self, request):
        data = request.POST
        for input, value in data.items():
            if input == "button_action_qonto":
                result = button_action_qonto(value)
                print(f'result {result}')
            elif input == "button_action_odoo":
                result = button_action_odoo(value)
                print(f'result {result}')

        return redirect('index')
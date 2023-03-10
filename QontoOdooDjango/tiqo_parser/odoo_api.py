import decimal

import json

from django.contrib.sites import requests
import requests
from tiqo_parser.models import Configuration, Label, AccountJournal, AccountAnalyticGroup, AccountAnalyticAccount
from tiqo_parser.serializers import LabelsSerializer

import logging

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


class OdooApi():
    def __init__(self):
        config = Configuration.get_solo()
        self.login = config.odoo_login
        self.api_key = config.odoo_apikey
        self.url = config.odoo_url
        self.odoo_dbname = config.odoo_dbname
        if not any([self.login, self.api_key, self.url, self.odoo_dbname]):
            raise Exception("Bad Odoo credentials. Set its in the admin panel.")

        self.params = {
            "db": f"{self.odoo_dbname}",
            "login": f"{self.login}",
            "apikey": f"{self.api_key}",
        }

    def test_config(self):
        url = f"{self.url}tibillet-api/xmlrpc/login"

        headers = {
            'content-type': 'application/json'
        }

        data = json.dumps({
            "params": self.params
        }, cls=DecimalEncoder)

        session = requests.session()
        response = session.post(url, data=data, headers=headers)
        session.close()

        if response.status_code == 200:
            resp_json = response.json()
            status = resp_json.get('result').get('authentification')
            if status == True:
                return status
            else:
                logging.error(f"Odoo server OFFLINE or BAD KEY : {resp_json}")
                return resp_json.get('result').get('error')

        return response

    def gc_contact(self, email: str, name: str):
        url = f"{self.url}tibillet-api/xmlrpc/gc_contact"
        headers = {
            'content-type': 'application/json'
        }

        # On ajoute les infos de membre au post DATA
        self.params["membre"] = {
            "name": f"{name.capitalize()}",
            "email": f"{email}"
        }

        data = json.dumps({
            "params": self.params,
        }, cls=DecimalEncoder)

        session = requests.session()
        response = session.post(url, data=data, headers=headers)
        session.close()
        return response.json()

    def create_draft_invoice(self, data: dict):
        url = f"{self.url}tibillet-api/xmlrpc/create_draft_invoice"
        headers = {
            'content-type': 'application/json'
        }

        # On ajoute les infos de membre au post DATA
        self.params["invoice_data"] = {'coucou': 'coucou'}

        data = json.dumps({
            "params": self.params,
        }, cls=DecimalEncoder)

        session = requests.session()
        response = session.post(url, data=data, headers=headers)
        session.close()
        response_json = response.json()
        print(response_json)

        return response_json

    def get_account_journal(self):
        url = f"{self.url}tibillet-api/xmlrpc/account_journal"

        headers = {
            'content-type': 'application/json'
        }

        data = json.dumps({
            "params": self.params
        }, cls=DecimalEncoder)

        session = requests.session()
        response = session.post(url, data=data, headers=headers)
        session.close()

        if response.status_code == 200:
            resp_json = response.json()
            for name, id_odoo in resp_json.get('result').items():
                print(f'{str(name)} : {int(id_odoo)}')
                AccountJournal.objects.get_or_create(
                    name=name,
                    id_odoo=id_odoo,
                )
            return AccountJournal.objects.all()

        raise Exception(f"Odoo server OFFLINE or BAD KEY : {response}")

    def get_account_analytic(self):
        url = f"{self.url}tibillet-api/xmlrpc/account_analytic"

        headers = {
            'content-type': 'application/json'
        }

        data = json.dumps({
            "params": self.params
        }, cls=DecimalEncoder)

        session = requests.session()
        response = session.post(url, data=data, headers=headers)
        session.close()

        if response.status_code == 200:
            resp_json = response.json()
            accounts = resp_json.get('result')
            for account in accounts:
                # On gère d'abord les groupes
                group = None
                if account.get('group_id'):
                    group, created = AccountAnalyticGroup.objects.get_or_create(
                        id_odoo=account.get('group_id')[0],
                        name=account.get('group_id')[1],
                    )

                # On gère ensuite les comptes analytiques
                account, created = AccountAnalyticAccount.objects.get_or_create(
                    id_odoo=account.get('id'),
                    name=account.get('name'),
                    code=account.get('code'),
                    group=group,
                )

            return AccountAnalyticAccount.objects.all()

        raise Exception(f"Odoo server OFFLINE or BAD KEY : {response}")

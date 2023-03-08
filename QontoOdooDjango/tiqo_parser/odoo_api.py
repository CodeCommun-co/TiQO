import decimal

import json

from django.contrib.sites import requests
import requests
from tiqo_parser.models import Configuration, Label, AccountJournal
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
        self.odoo_database = config.odoo_dbname
        if not any([self.login, self.api_key]):
            raise Exception("No Qonto credentials. Set its in the admin panel.")

        self.params = {
                "db": f"{self.odoo_database}",
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
            else :
                logging.error(f"Odoo server OFFLINE or BAD KEY : {resp_json}")
                return resp_json.get('result').get('error')

        return response

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
                print(f'{name} : {id_odoo}')
                AccountJournal.objects.get_or_create(
                    name=name,
                    id_odoo=id_odoo,
                )
            return AccountJournal.objects.all()

            # AccountJournal

        return response
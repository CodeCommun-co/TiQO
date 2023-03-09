from django.contrib.sites import requests
import requests
from tiqo_parser.models import Configuration, Label, Iban, Transaction, Category
from tiqo_parser.serializers import LabelsSerializer


class QontoApi():
    def __init__(self):
        config = Configuration.get_solo()
        self.login = config.qonto_login
        self.api_key = config.qonto_apikey

        if not any([self.login, self.api_key]):
            raise Exception("No Qonto credentials. Set its in the admin panel.")

    def _get_request_api(self, url, params=None):
        url = f"https://thirdparty.qonto.com/v2/{url}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.login}:{self.api_key}"
        }

        response = requests.request("GET", url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()

        print(response.text)
        raise Exception(response.text)

    def get_ibans(self):
        info_orga = self._get_request_api("organization")
        if info_orga.get('organization'):
            if info_orga.get('organization').get('bank_accounts'):
                bank_accounts = info_orga.get('organization').get('bank_accounts')
                for acc in bank_accounts:
                    Iban.objects.get_or_create(
                        iban=acc.get('iban'),
                        name=acc.get('name'),
                    )

        return Iban.objects.all()

    def get_last100_transaction(self):
        # Mise à jour des IBAN
        ibans = self.get_ibans()

        transactions = {}
        # Qonto demande l'iban du compte pour récupérer les transactions
        for iban in ibans:
            response_dict = self._get_request_api("transactions", params={"iban": iban.iban})
            if response_dict :
                transactions[iban] = response_dict.get('transactions')


        for iban, transactions in transactions.items():
            for transaction in transactions:
                try :
                    tr_db = Transaction.objects.get(
                        uuid=transaction.get('id'),
                        transaction_id=transaction.get('transaction_id'),
                        iban=iban
                    )
                    #TODO: Update ?
                except Transaction.DoesNotExist:
                    category = Category.objects.get_or_create(name=transaction.get('category'))[0]
                    tr_db = Transaction.objects.create(
                        uuid=transaction.get('id'),
                        transaction_id=transaction.get('transaction_id'),
                        iban=iban,
                        emitted_at=transaction.get('emitted_at'),
                        status=transaction.get('status'),
                        amount_cents=transaction.get('amount_cents', 0),
                        currency=transaction.get('currency', 'EUR'),
                        note=transaction.get('note'),
                        label=transaction.get('label'),
                        vat_amount_cents=transaction.get('vat_amount_cents', 0),
                        initiator_id=transaction.get('initiator_id'),
                        card_last_digits=transaction.get('card_last_digits'),
                        category=category,
                    )

        return Transaction.objects.all()

    def get_labels(self):

        labels_qonto = self._get_request_api("labels")
        labels = labels_qonto.get('labels')

        # On crée les labels qui n'ont pas de parent en premier
        parents = [label for label in labels if not label.get('parent_id')]
        for label in parents:
            labeldb, created = Label.objects.get_or_create(
                uuid=label.get('id'),
                name=label.get('name'),
            )

        # On crée les labels qui ont un parent
        childs = [label for label in labels if label.get('parent_id')]
        for label in childs:
            labeldb, created = Label.objects.get_or_create(
                uuid=label.get('id'),
                name=label.get('name'),
            )

            label_parent = Label.objects.get(uuid=label.get('parent_id'))
            labeldb.parent = label_parent
            labeldb.save()

        return LabelsSerializer(Label.objects.all())

import uuid

from django.conf import settings
from django.contrib.sites import requests
import requests
import pathlib, os, json
from django.template.defaultfilters import slugify

from tiqo_parser.models import Configuration, Label, Iban, Transaction, Category, Contact, Attachment
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

    def get_membership(self):
        response_dict = self._get_request_api("memberships")
        members = response_dict.get('memberships')
        for member in members:
            Contact.objects.get_or_create(
                uuid=member.get('id'),
                last_name=member.get('last_name'),
                first_name=member.get('first_name'),
            )
        return Contact.objects.all()

    def fetch_last100_transaction(self):
        # Mise à jour des IBAN
        ibans = self.get_ibans()

        transactions = {}
        # Qonto demande l'iban du compte pour récupérer les transactions
        for iban in ibans:
            response_dict = self._get_request_api("transactions", params={"iban": iban.iban})
            if response_dict:
                transactions[iban] = response_dict.get('transactions')

        return transactions

    def download_attachment(self, uuid_attachment: str, db_transaction: Transaction):
        # On va chercher l'attachment dans la base de données
        # Peut être qu'il existe déja
        if Attachment.objects.filter(uuid=uuid_attachment).exists():
            db_attachement = Attachment.objects.get(uuid=uuid_attachment)
            db_attachement.transactions.add(db_transaction)
            print(f"EXIST attachment uuid : {db_attachement.name}")
            return db_attachement
        else :
            response_dict = self._get_request_api(f"attachments/{uuid_attachment}")
            attachment = response_dict.get('attachment')

            if attachment:
                file_content_type = attachment.get('file_content_type')
                file_ext = file_content_type.partition('/')[-1]
                file_name = f"{attachment['id']}.{file_ext}"
                url = attachment.get('url')

                fetch_file_url = requests.get(url)
                print(f"fetch_file_url.status_code : {fetch_file_url.status_code}")

                if fetch_file_url.status_code == 200:
                    path_media = f"{settings.MEDIA_ROOT}/" \
                                 f"{slugify(db_transaction.iban.name)}/" \
                                 f"{slugify(db_transaction.emitted_at.date())}/" \
                                 f"{db_transaction.side}/" \
                                 f"{db_transaction.uuid}/"

                    path = pathlib.Path(path_media)
                    pathlib.Path(f"{path_media}").mkdir(parents=True, exist_ok=True)

                    full_path_file = f"{path}/{file_name}"
                    with open(full_path_file, 'wb') as f:
                        f.write(fetch_file_url.content)

                    db_attachement, created = Attachment.objects.get_or_create(
                        uuid=attachment['id'],
                        filepath=full_path_file,
                        name=attachment['file_name'],
                    )
                    db_attachement.transactions.add(db_transaction)
                    print(f"NEW attachement downloaded : {db_attachement.name}")
                    return db_attachement



    def get_transactions(self):
        transactions = self.fetch_last100_transaction()
        contacts = self.get_membership()

        for iban, transactions in transactions.items():
            for transaction in transactions:
                try:
                    tr_db = Transaction.objects.get(
                        uuid=transaction.get('id'),
                        transaction_id=transaction.get('transaction_id'),
                        iban=iban
                    )
                    # TODO: Update ?
                except Transaction.DoesNotExist:
                    category = Category.objects.get_or_create(name=transaction.get('category'))[0]
                    side = 'C' if transaction.get('side') == 'credit' else 'D'

                    initiator = transaction.get('initiator_id')
                    if initiator:
                        initiator = contacts.get(uuid=initiator)

                    tr_db = Transaction.objects.create(
                        uuid=transaction.get('id'),
                        transaction_id=transaction.get('transaction_id'),
                        side=side,
                        iban=iban,
                        emitted_at=transaction.get('emitted_at'),
                        status=transaction.get('status'),
                        amount_cents=transaction.get('amount_cents', 0),
                        currency=transaction.get('currency', 'EUR'),
                        note=transaction.get('note'),
                        label=transaction.get('label'),
                        vat_amount_cents=transaction.get('vat_amount_cents', 0),
                        initiator_id=initiator,
                        card_last_digits=transaction.get('card_last_digits'),
                        category=category,
                    )

                    # On valide et raffraichi depuis la db, paske sinon les valeurs plus haut sont toujours des strings...
                    tr_db.refresh_from_db()
                    for attachment_id in transaction.get('attachment_ids', []):
                        self.download_attachment(attachment_id, tr_db)

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

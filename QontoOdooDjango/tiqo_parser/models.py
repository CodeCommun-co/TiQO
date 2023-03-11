import uuid
from django.conf import settings
from django.db import models
from solo.models import SingletonModel


# Create your models here.


class Configuration(SingletonModel):
    qonto_login = models.CharField(max_length=100)
    qonto_apikey = models.CharField(max_length=100)

    odoo_url = models.URLField()
    odoo_login = models.CharField(max_length=100)
    odoo_apikey = models.CharField(max_length=100)
    odoo_dbname = models.CharField(max_length=100)


### ODOO TABLE

class OdooContact(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    id_odoo = models.SmallIntegerField()
    email = models.EmailField(blank=True, null=True)
    type = models.CharField(choices=(('M', 'membership'), ('B', 'beneficiarie')), max_length=1)

    def __str__(self):
        if self.email and self.name:
            return f"{self.name} ({self.email})"
        return self.name

class AccountJournal(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    id_odoo = models.SmallIntegerField()

    def __str__(self):
        return self.name


class AccountAnalyticGroup(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    id_odoo = models.SmallIntegerField()

    def __str__(self):
        return self.name


class AccountAnalyticAccount(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    id_odoo = models.SmallIntegerField()
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    group = models.ForeignKey(AccountAnalyticGroup, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.group:
            return f"{self.group.name} > {self.name}"
        return self.name


### QONTO TABLE
class Iban(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    iban = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Label(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    # Liaison avec Odoo :
    odoo_analytic_account = models.ForeignKey(AccountAnalyticAccount, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class QontoContact(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    type = models.CharField(choices=(('M', 'membership'), ('B', 'beneficiarie')), max_length=1)

    odoo_contact = models.ForeignKey(OdooContact, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name[0].upper()}."
        return self.last_name if self.last_name else self.first_name


class Category(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    transaction_id = models.CharField(max_length=100)

    iban = models.ForeignKey(Iban, on_delete=models.CASCADE)
    emitted_at = models.DateTimeField()
    side = models.CharField(choices=(('D', 'debit'), ('C', 'credit')), max_length=1)

    status = models.CharField(max_length=100)
    amount_cents = models.IntegerField()
    currency = models.CharField(max_length=3)
    note = models.TextField(blank=True, null=True)
    label = models.CharField(max_length=100, null=True, blank=True)
    vat_amount_cents = models.IntegerField(default=0, null=True, blank=True)

    initiator = models.ForeignKey(QontoContact, on_delete=models.CASCADE, null=True, blank=True, related_name='initiator_transactions')
    card_last_digits = models.CharField(max_length=4, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    label_ids = models.ManyToManyField(Label, related_name='transactions')

    # Les transactions qui vont vers des comptes externes ( virements )
    uuid_external_transfer = models.UUIDField(null=True, blank=True)
    beneficiary = models.ForeignKey(QontoContact, on_delete=models.CASCADE, null=True, blank=True, related_name='beneficiary_transactions')
    reference = models.TextField(null=True, blank=True)

class Attachment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    transactions = models.ManyToManyField(Transaction, related_name='attachments')
    filepath = models.FilePathField(path=settings.MEDIA_ROOT, recursive=True, allow_folders=True, allow_files=True, blank=True, null=True)
    url_qonto = models.URLField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

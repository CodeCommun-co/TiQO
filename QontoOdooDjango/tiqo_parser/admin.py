from django.contrib import admin, messages
from solo.admin import SingletonModelAdmin
from .models import Configuration, AccountJournal, Category, Label, QontoContact, Transaction, Iban, Attachment, \
    OdooArticles, AccountAnalyticAccount
from .odoo_api import OdooApi
from .qonto_api import QontoApi

admin.site.site_header = 'TiQO : Qonto X Odoo - Administration'


# Register your models here.
class ConfigurationAdmin(SingletonModelAdmin):
    def save_model(self, request, obj, form, change):
        obj: Configuration
        odoo_api = OdooApi()
        test_result = odoo_api.test_config()
        if test_result == True:
            messages.add_message(request, messages.INFO, f"Configuration ODOO {test_result}")
        else:
            messages.add_message(request, messages.ERROR, f"Odoo error : {test_result}")

        super().save_model(request, obj, form, change)


admin.site.register(Configuration, ConfigurationAdmin)


# class IbanAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'iban',
#     )
#     ordering = ('name',)
#
# admin.site.register(Iban, IbanAdmin)

class LabelADmin(admin.ModelAdmin):
    change_list_template = 'custom_admin/labelqonto_changelist.html'

    list_display = (
        'parent',
        'name',
        'odoo_article',
        'odoo_analytic_account',
        'odoo_journal_account',
        'odoo_account_account',
    )

    list_editable = (
        'odoo_article',
        'odoo_analytic_account',
        'odoo_journal_account',
        'odoo_account_account',
    )

    ordering = ('parent__name', 'name')

    def get_queryset(self, request):
        qs = super(LabelADmin, self).get_queryset(request)
        qs = qs.exclude(parent__isnull=True)
        return qs

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(Label, LabelADmin)


def action_create_draft_invoice(modeladmin, request, queryset):
    for transaction in queryset:
        transaction: Transaction

        if not transaction.odoo_article():
            messages.add_message(request, messages.ERROR,
                                 f"Transaction {transaction} : Pas d'article lié au tag Qonto. "
                                 f"Merci de lier l'article à l'un des labels Qonto")
        if not transaction.beneficiary or not transaction.initiator:
            messages.add_message(request, messages.ERROR,
                                 f"Transaction {transaction} : Pas de donneur d'ordre ou de bénéficiaire. "
                                 f"Merci de renseigner les champs dans la liste des transactions")

        if transaction.odoo_sended:
            messages.add_message(request, messages.WARNING,
                                 f"Transaction {transaction} : Facture déjà envoyée à Odoo. Cela va créer un doublon ! (mais en brouillon ...) ")
            # return False

        if transaction.beneficiary and transaction.initiator:
            if not transaction.beneficiary.odoo_contact or not transaction.initiator.odoo_contact:
                messages.add_message(request, messages.ERROR,
                                     f"Pas de contact Odoo relié au bénéficiaire ou à l'initiateur de la transaction. "
                                     f"Merci de renseigner les champs dans la liste des contacts Qonto")

            else :
                odoo_api = OdooApi()
                qonto_api = QontoApi()

                article: OdooArticles = transaction.odoo_article()
                compte_analytique: AccountAnalyticAccount = transaction.odoo_analytic_account()
                journal: AccountJournal = transaction.odoo_journal_account()
                beneficiary = transaction.beneficiary.odoo_contact.id_odoo
                initiator = transaction.initiator.odoo_contact.id_odoo

                # Mise à jour des url qonto. Ils ne sont valides que 24h
                for attachment in transaction.attachments.all():
                    attachment = qonto_api.download_or_update_attachment(attachment.uuid, transaction)

                response = odoo_api.create_draft_invoice(transaction)

                if response.get('result'):
                    # return {'status': True, 'invoice_draft_id': invoice_draft_id, 'article_added': article_added}
                    if response.get('result').get('status'):
                        messages.add_message(request, messages.INFO, f"{response}")
                else:
                    messages.add_message(request, messages.ERROR, f"{response}")



class TransactionsAdmin(admin.ModelAdmin):
    change_list_template = 'custom_admin/transactions_changelist.html'
    list_display = (
        "label",
        "iban",
        "side",
        "emitted_at",
        "amount_cents",
        "initiator",
        "beneficiary",
        "as_attachment",
        "odoo_sended",
        "label_ids_string",
        "odoo_article",
    )

    list_filter = (
        "iban",
        "side",
        "initiator",
        "beneficiary",
    )

    search_fields = (
        "label",
    )
    actions = [action_create_draft_invoice, ]

    ordering = ('iban', 'side', 'emitted_at')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


admin.site.register(Transaction, TransactionsAdmin)


def button_action_create_odoo_contact(modeladmin, request, queryset):
    for qonto_contact in queryset:
        email = qonto_contact.email
        name = qonto_contact.name()

        if not email:
            messages.add_message(request, messages.ERROR, f"Pas d'email pour {name}. Compte Odoo non créé.")
        else:
            odooApi = OdooApi()
            response_odoo = odooApi.gc_contact(email, name)
            if response_odoo.get('result'):
                all_odoo_contacts = odooApi.get_all_contacts()
                odoo_contact = all_odoo_contacts.get(email=email)
                qonto_contact.email = email
                qonto_contact.odoo_contact = odoo_contact
                qonto_contact.save()


button_action_create_odoo_contact.short_description = "Envoyer vers Odoo"


class QontoContactAdmin(admin.ModelAdmin):
    change_list_template = 'custom_admin/qontocontact_changelist.html'
    list_display = (
        "name",
        "email",
        "type",
        "odoo_contact",
    )
    list_filter = (
        "type",
        "odoo_contact",
    )
    ordering = ('first_name',)
    list_editable = ("email", "odoo_contact",)
    actions = [button_action_create_odoo_contact, ]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    # def save_model(self, request, obj, form, change):
    #     Si pas d'email mais un contact Odoo, on récupère l'email du contact Odoo
    # if not obj.email and obj.odoo_contact:
    #     obj.email = obj.odoo_contact.email
    #     obj.save()


admin.site.register(QontoContact, QontoContactAdmin)

from django.contrib import admin, messages
from solo.admin import SingletonModelAdmin
from .models import Configuration, AccountJournal, Category, Label, Contact, Transaction, Iban
from .odoo_api import OdooApi


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

class IbanAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'iban',
    )
    ordering = ('name',)

admin.site.register(Iban, IbanAdmin)

class LabelADmin(admin.ModelAdmin):
    list_display = (
        'parent',
        'name',
        'odoo_analytic_account',
    )
    ordering = ('parent__name', 'name')

admin.site.register(Label, LabelADmin)


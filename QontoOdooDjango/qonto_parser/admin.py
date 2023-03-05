from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Configuration, Account, Category, Label, Contact, Transaction

# Register your models here.
class ConfigurationAdmin(SingletonModelAdmin):
    pass
admin.site.register(Configuration, ConfigurationAdmin)


admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Label)
admin.site.register(Contact)
admin.site.register(Transaction)


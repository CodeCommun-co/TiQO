from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import Configuration, Account, Category, Label, Contact, Transaction

# Register your models here.
class ConfigurationAdmin(SingletonModelAdmin):
    pass
admin.site.register(Configuration, ConfigurationAdmin)


class LabelADmin(admin.ModelAdmin):
    list_display = (
        'parent',
        'name',
    )
    ordering = ('parent__name', 'name')

admin.site.register(Label, LabelADmin)


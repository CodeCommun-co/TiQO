# Generated by Django 4.1.7 on 2023-03-13 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tiqo_parser', '0025_alter_label_options_alter_qontocontact_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='iban',
            options={'verbose_name': 'Compte Qonto', 'verbose_name_plural': 'Comptes Qonto'},
        ),
        migrations.AddField(
            model_name='transaction',
            name='odoo_invoice_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='odoo_sended',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount_cents',
            field=models.IntegerField(verbose_name='Montant (cts)'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='beneficiary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='beneficiary_transactions', to='tiqo_parser.qontocontact', verbose_name='Bénéficiaire'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='emitted_at',
            field=models.DateTimeField(verbose_name='Emission'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='iban',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tiqo_parser.iban', verbose_name='Compte'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='initiator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='initiator_transactions', to='tiqo_parser.qontocontact', verbose_name='Initiateur'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='label',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Libellé'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='side',
            field=models.CharField(choices=[('D', 'debit'), ('C', 'credit')], max_length=1, verbose_name='Sens'),
        ),
    ]

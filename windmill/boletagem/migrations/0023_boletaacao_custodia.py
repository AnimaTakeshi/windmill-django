# Generated by Django 2.0 on 2018-10-16 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0012_cpr_fundo'),
        ('boletagem', '0022_auto_20181015_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='boletaacao',
            name='custodia',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='fundo.Custodiante'),
            preserve_default=False,
        ),
    ]

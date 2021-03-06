# Generated by Django 2.0 on 2018-10-18 16:41

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0013_auto_20181018_1341'),
        ('fundo', '0013_auto_20181018_1102'),
        ('boletagem', '0027_boletafundooffshore_fechada'),
    ]

    operations = [
        migrations.AddField(
            model_name='boletapassivo',
            name='cota',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='boletapassivo',
            name='cotista',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='fundo.Cotista'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='boletapassivo',
            name='data_cotizacao',
            field=models.DateField(default=datetime.date(2018, 10, 18)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='boletapassivo',
            name='data_liquidacao',
            field=models.DateField(default=datetime.date(2018, 10, 18)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='boletapassivo',
            name='data_movimentacao',
            field=models.DateField(default=datetime.date(2018, 10, 18)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='boletapassivo',
            name='fundo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='ativos.Ativo'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='boletapassivo',
            name='valor',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=13),
            preserve_default=False,
        ),
    ]

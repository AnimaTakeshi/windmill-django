# Generated by Django 2.0 on 2018-10-18 16:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0012_caixa_custodia'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundo_offshore',
            name='data_cotizacao_aplicacao',
            field=models.DateField(default=datetime.date(2018, 10, 18)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fundo_offshore',
            name='data_cotizacao_resgate',
            field=models.DateField(default=datetime.date(2018, 10, 18)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fundo_offshore',
            name='data_liquidacao_aplicacao',
            field=models.DateField(default=datetime.date(2018, 10, 18)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fundo_offshore',
            name='data_liquidacao_resgate',
            field=models.DateField(default=datetime.date(2018, 10, 18)),
            preserve_default=False,
        ),
    ]
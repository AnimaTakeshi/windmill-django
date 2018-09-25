# Generated by Django 2.1 on 2018-09-21 19:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boletagem', '0004_auto_20180921_1200'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='boletarendafixalocal',
            options={'verbose_name_plural': 'Boletas de operação de renda fixa local'},
        ),
        migrations.AddField(
            model_name='boletafundolocal',
            name='preco',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='boletafundolocal',
            name='quantidade',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=15),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='boletafundooffshore',
            name='data_operacao',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='boletarendafixalocal',
            name='taxa',
            field=models.DecimalField(decimal_places=6, max_digits=10),
        ),
    ]

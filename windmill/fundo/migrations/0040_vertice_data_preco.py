# Generated by Django 2.0 on 2019-02-04 12:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0039_auto_20181217_0854'),
    ]

    operations = [
        migrations.AddField(
            model_name='vertice',
            name='data_preco',
            field=models.DateField(default=datetime.date(1900, 1, 1)),
            preserve_default=False,
        ),
    ]

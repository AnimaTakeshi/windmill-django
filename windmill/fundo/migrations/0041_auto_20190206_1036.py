# Generated by Django 2.0 on 2019-02-06 12:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0040_vertice_data_preco'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vertice',
            name='data_preco',
            field=models.DateField(default=datetime.date.today),
        ),
    ]

# Generated by Django 2.0 on 2018-12-10 16:25

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0034_fundo_data_exercicio_social'),
    ]

    operations = [
        migrations.AddField(
            model_name='vertice',
            name='cambio',
            field=models.DecimalField(decimal_places=6, default=Decimal('1'), max_digits=12),
        ),
    ]

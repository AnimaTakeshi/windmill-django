# Generated by Django 2.0 on 2018-10-17 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boletagem', '0025_auto_20181016_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boletarendafixaoffshore',
            name='taxa',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=8, null=True),
        ),
    ]
# Generated by Django 2.0 on 2018-10-26 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boletagem', '0044_auto_20181026_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boletapassivo',
            name='cota',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=15, null=True),
        ),
    ]
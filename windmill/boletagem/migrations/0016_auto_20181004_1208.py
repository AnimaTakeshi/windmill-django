# Generated by Django 2.0 on 2018-10-04 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boletagem', '0015_auto_20181002_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boletaprovisao',
            name='financeiro',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]
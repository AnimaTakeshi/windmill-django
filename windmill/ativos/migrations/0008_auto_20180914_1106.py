# Generated by Django 2.1 on 2018-09-14 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0007_auto_20180914_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ativo',
            name='bbg_ticker',
            field=models.CharField(blank=True, default=None, max_length=25, null=True, unique=True),
        ),
    ]
# Generated by Django 2.0 on 2018-10-26 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0019_auto_20181023_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cpr',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
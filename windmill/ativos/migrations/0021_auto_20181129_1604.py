# Generated by Django 2.0 on 2018-11-29 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0020_auto_20181112_1439'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fundo_local',
            old_name='CPNJ',
            new_name='CNPJ',
        ),
    ]

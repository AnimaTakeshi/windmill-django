# Generated by Django 2.0 on 2018-10-19 18:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boletagem', '0033_auto_20181019_1500'),
    ]

    operations = [
        migrations.RenameField(
            model_name='boletapassivo',
            old_name='content_type',
            new_name='boleta_type',
        ),
    ]

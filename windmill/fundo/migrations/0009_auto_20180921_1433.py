# Generated by Django 2.1 on 2018-09-21 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0008_auto_20180921_1402'),
    ]

    operations = [
        migrations.RenameField(
            model_name='quantidade',
            old_name='quantidade',
            new_name='qtd',
        ),
    ]
# Generated by Django 2.1 on 2018-09-18 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0003_auto_20180917_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contato',
            name='area',
            field=models.CharField(max_length=50),
        ),
    ]
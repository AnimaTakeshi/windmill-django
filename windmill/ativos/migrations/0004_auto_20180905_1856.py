# Generated by Django 2.1.1 on 2018-09-05 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0003_auto_20180905_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acao',
            name='tipo',
            field=models.CharField(choices=[('PN', 'Preferencial'), ('ON', 'Ordinária')], max_length=20, null=True),
        ),
    ]
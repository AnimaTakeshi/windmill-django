# Generated by Django 2.1 on 2018-09-12 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0004_cambio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acao',
            name='tipo',
            field=models.CharField(choices=[('PN', 'PN'), ('ON', 'ON')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='renda_fixa',
            name='info',
            field=models.CharField(choices=[('PU', 'PU'), ('Yield', 'Yield')], default='PU', max_length=3, verbose_name='informacao de mercado'),
        ),
    ]

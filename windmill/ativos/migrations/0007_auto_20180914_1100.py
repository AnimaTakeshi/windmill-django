# Generated by Django 2.1 on 2018-09-14 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0006_auto_20180912_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ativo',
            name='bbg_ticker',
            field=models.CharField(blank=True, max_length=25, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='renda_fixa',
            name='info',
            field=models.CharField(choices=[('PU', 'PU'), ('Yield', 'Yield')], default='PU', max_length=3, verbose_name='informação de mercado'),
        ),
        migrations.AlterField(
            model_name='renda_fixa',
            name='periodo',
            field=models.IntegerField(default=0, verbose_name='periodicidade do cupom em meses'),
        ),
    ]

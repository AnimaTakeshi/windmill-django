# Generated by Django 2.1 on 2018-09-11 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0002_auto_20180906_1734'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='acao',
            options={'verbose_name_plural': 'Ações'},
        ),
        migrations.AlterModelOptions(
            name='ativo',
            options={'ordering': ['nome'], 'verbose_name_plural': 'Ativos'},
        ),
        migrations.AlterModelOptions(
            name='moeda',
            options={'verbose_name_plural': 'Moedas'},
        ),
        migrations.AlterModelOptions(
            name='pais',
            options={'verbose_name_plural': 'Países'},
        ),
        migrations.AlterModelOptions(
            name='renda_fixa',
            options={'verbose_name_plural': 'Ativos de Renda Fixa'},
        ),
        migrations.AlterField(
            model_name='ativo',
            name='bbg_ticker',
            field=models.CharField(blank=True, max_length=25, null=True, unique=True),
        ),
    ]

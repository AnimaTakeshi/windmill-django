# Generated by Django 2.0 on 2018-12-11 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0004_auto_20181112_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preco',
            name='preco_contabil',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='preco',
            name='preco_estimado',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='preco',
            name='preco_fechamento',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='preco',
            name='preco_gerencial',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=15, null=True),
        ),
    ]

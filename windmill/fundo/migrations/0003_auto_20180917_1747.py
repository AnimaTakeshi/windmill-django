# Generated by Django 2.1 on 2018-09-17 20:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0002_auto_20180917_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundo',
            name='capitalizacao_taxa_adm',
            field=models.CharField(blank=True, choices=[('Diária', 'Diária'), ('Mensal', 'Mensal')], max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='fundo',
            name='categoria',
            field=models.CharField(blank=True, choices=[('Fundo de Ações', 'Fundo de Ações'), ('Fundo Multimercado', 'Fundo Multimercado'), ('Fundo Imobiliário', 'Fundo Imobiliário'), ('Fundo de Renda Fixa', 'Fundo de Renda Fixa')], max_length=40, null=True, verbose_name='Categoria do Fundo'),
        ),
        migrations.AlterField(
            model_name='fundo',
            name='data_de_inicio',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='fundo',
            name='distribuidora',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='fundo.Distribuidora'),
        ),
        migrations.AlterField(
            model_name='fundo',
            name='gestora',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='fundo.Gestora'),
        ),
        migrations.AlterField(
            model_name='fundo',
            name='taxa_administracao',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=7, null=True, verbose_name='Taxa de Administração'),
        ),
    ]
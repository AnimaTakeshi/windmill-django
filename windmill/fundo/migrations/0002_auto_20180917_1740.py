# Generated by Django 2.1 on 2018-09-17 20:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundo',
            name='capitalizacao_taxa_adm',
            field=models.CharField(choices=[('Diária', 'Diária'), ('Mensal', 'Mensal')], max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='fundo',
            name='gestora',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='fundo.Gestora'),
        ),
        migrations.AlterField(
            model_name='fundo',
            name='taxa_administracao',
            field=models.DecimalField(decimal_places=5, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='fundo',
            name='data_de_inicio',
            field=models.DateField(null=True),
        ),
    ]

# Generated by Django 2.1.1 on 2018-09-04 12:33

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Moeda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=15, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=20, unique=True)),
                ('moeda', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ativos.Moeda')),
            ],
        ),
        migrations.CreateModel(
            name='Renda_Fixa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=25, unique=True)),
                ('bbg_ticker', models.CharField(max_length=25, unique=True)),
                ('tipo_ativo', models.CharField(choices=[('RV', 'Ações'), ('RF', 'Renda Fixa'), ('RE', 'Real Estate'), ('FRV', 'Fundo de Renda Variável'), ('FRF', 'Fundo de Renda Fixa'), ('FII', 'Fundo Imobiliário')], default='RV', max_length=5)),
                ('vencimento', models.DateField(default=datetime.date(9999, 12, 31))),
                ('pais', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ativos.Pais')),
            ],
            options={
                'ordering': ['nome'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='moeda',
            name='codigo',
            field=models.CharField(default=1, max_length=3, unique=True),
            preserve_default=False,
        ),
    ]

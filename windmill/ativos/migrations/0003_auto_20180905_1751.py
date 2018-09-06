# Generated by Django 2.1.1 on 2018-09-05 20:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0002_auto_20180905_1642'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=25, unique=True)),
                ('bbg_ticker', models.CharField(max_length=25, null=True, unique=True)),
                ('tipo', models.CharField(choices=[('PN', 'Preferencial'), ('ON', 'Ordinária')], max_length=20)),
                ('pais', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='ativos.Pais')),
            ],
            options={
                'ordering': ['nome'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='renda_fixa',
            name='tipo_ativo',
        ),
        migrations.AddField(
            model_name='renda_fixa',
            name='cupom',
            field=models.DecimalField(decimal_places=5, default=0, max_digits=7, null=True),
        ),
        migrations.AddField(
            model_name='renda_fixa',
            name='info',
            field=models.CharField(choices=[('PU', 'PU'), ('YLD', 'Yield')], default='PU', max_length=3, verbose_name='informacao de mercado'),
        ),
        migrations.AddField(
            model_name='renda_fixa',
            name='periodo',
            field=models.IntegerField(default=0, verbose_name='periodicidade do cupom'),
        ),
        migrations.AlterField(
            model_name='renda_fixa',
            name='bbg_ticker',
            field=models.CharField(max_length=25, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='renda_fixa',
            name='pais',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='ativos.Pais'),
        ),
    ]
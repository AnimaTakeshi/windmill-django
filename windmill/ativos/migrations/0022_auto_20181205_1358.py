# Generated by Django 2.0 on 2018-12-05 15:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ativos', '0021_auto_20181129_1604'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='caixa',
            name='moeda',
        ),
        migrations.AddField(
            model_name='ativo',
            name='moeda',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ativos.Moeda'),
        ),
    ]

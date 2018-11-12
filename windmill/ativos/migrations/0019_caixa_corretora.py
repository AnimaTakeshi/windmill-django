# Generated by Django 2.0 on 2018-11-08 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0029_auto_20181108_1100'),
        ('ativos', '0018_ativo_descricao'),
    ]

    operations = [
        migrations.AddField(
            model_name='caixa',
            name='corretora',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='fundo.Corretora'),
            preserve_default=False,
        ),
    ]

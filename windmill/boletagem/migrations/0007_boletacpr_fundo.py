# Generated by Django 2.1 on 2018-09-24 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0009_auto_20180921_1433'),
        ('boletagem', '0006_boletaprovisao_descricao'),
    ]

    operations = [
        migrations.AddField(
            model_name='boletacpr',
            name='fundo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='fundo.Fundo'),
            preserve_default=False,
        ),
    ]
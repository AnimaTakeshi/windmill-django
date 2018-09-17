# Generated by Django 2.1 on 2018-09-17 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('boletagem', '0001_initial'),
        ('fundo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='boleta_acao',
            name='corretora',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='fundo.Corretora'),
        ),
    ]
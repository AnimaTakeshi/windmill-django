# Generated by Django 2.0 on 2018-11-05 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calendario', '0001_initial'),
        ('fundo', '0027_auto_20181101_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundo',
            name='calendario',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='calendario.Calendario'),
            preserve_default=False,
        ),
    ]

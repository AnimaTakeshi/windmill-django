# Generated by Django 2.0 on 2018-10-05 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0011_auto_20181002_1446'),
    ]

    operations = [
        migrations.AddField(
            model_name='cpr',
            name='fundo',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.PROTECT, to='fundo.Fundo'),
            preserve_default=False,
        ),
    ]

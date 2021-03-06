# Generated by Django 2.0 on 2018-10-19 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0017_auto_20181019_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotista',
            name='fundo_cotista',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='fundo.Fundo', unique=True),
        ),
        migrations.AlterField(
            model_name='cotista',
            name='nome',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]

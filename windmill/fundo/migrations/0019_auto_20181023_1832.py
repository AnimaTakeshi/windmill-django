# Generated by Django 2.0 on 2018-10-23 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0018_auto_20181019_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotista',
            name='fundo_cotista',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='fundo.Fundo'),
        ),
    ]

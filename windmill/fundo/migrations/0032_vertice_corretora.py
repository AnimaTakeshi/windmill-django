# Generated by Django 2.0 on 2018-11-29 19:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0031_auto_20181129_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='vertice',
            name='corretora',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='fundo.Corretora'),
        ),
    ]

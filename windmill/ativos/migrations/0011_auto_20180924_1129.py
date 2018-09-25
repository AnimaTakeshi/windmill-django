# Generated by Django 2.1 on 2018-09-24 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0009_auto_20180921_1433'),
        ('ativos', '0010_auto_20180920_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundo_local',
            name='gerido',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='fundo.Fundo'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fundo_offshore',
            name='gerido',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='fundo.Fundo'),
            preserve_default=False,
        ),
    ]

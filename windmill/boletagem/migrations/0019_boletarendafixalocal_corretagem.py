# Generated by Django 2.0 on 2018-10-08 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boletagem', '0018_boletaacao_corretagem'),
    ]

    operations = [
        migrations.AddField(
            model_name='boletarendafixalocal',
            name='corretagem',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=13),
            preserve_default=False,
        ),
    ]

# Generated by Django 2.0 on 2018-10-25 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boletagem', '0041_auto_20181023_1915'),
    ]

    operations = [
        migrations.AddField(
            model_name='boletaprovisao',
            name='estado',
            field=models.CharField(choices=[('Pendente', 'Pendente'), ('Liquidado', 'Liquidado')], default='Pendente', max_length=9),
        ),
    ]

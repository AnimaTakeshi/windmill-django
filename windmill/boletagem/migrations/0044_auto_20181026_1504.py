# Generated by Django 2.0 on 2018-10-26 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boletagem', '0043_auto_20181025_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boletacpr',
            name='capitalizacao',
            field=models.CharField(choices=[('Diária', 'Diária'), ('Mensal', 'Mensal'), ('Nenhuma', 'Nenhuma')], default='Nenhuma', max_length=7),
        ),
        migrations.AlterField(
            model_name='boletacpr',
            name='tipo',
            field=models.CharField(choices=[('Diarização', 'Diarização'), ('Diferimento', 'Diferimento'), ('CPR', 'CPR')], default='CPR', max_length=12),
        ),
    ]
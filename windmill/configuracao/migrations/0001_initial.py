# Generated by Django 2.0 on 2018-12-10 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fundo', '0034_fundo_data_exercicio_social'),
        ('ativos', '0022_auto_20181205_1358'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigCambio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cambio', models.ManyToManyField(to='ativos.Cambio')),
                ('fundo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fundo.Fundo')),
            ],
        ),
    ]

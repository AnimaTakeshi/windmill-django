# Generated by Django 2.0 on 2018-11-07 21:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0002_provento'),
    ]

    operations = [
        migrations.AddField(
            model_name='provento',
            name='data_com',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='provento',
            name='direito_por_acao',
            field=models.DecimalField(blank=True, decimal_places=9, default=None, max_digits=11, null=True),
        ),
    ]

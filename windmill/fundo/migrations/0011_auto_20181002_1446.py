# Generated by Django 2.0 on 2018-10-02 17:46

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ativos', '0011_auto_20180924_1129'),
        ('fundo', '0010_auto_20180926_1913'),
    ]

    operations = [
        migrations.AddField(
            model_name='cpr',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='boleta', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='cpr',
            name='data',
            field=models.DateField(default=datetime.date(2018, 10, 2)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cpr',
            name='descricao',
            field=models.CharField(default='Despesa', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cpr',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cpr',
            name='valor',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fundo',
            name='caixa_padrao',
            field=models.ForeignKey(default=16, on_delete=django.db.models.deletion.PROTECT, to='ativos.Caixa'),
            preserve_default=False,
        ),
    ]

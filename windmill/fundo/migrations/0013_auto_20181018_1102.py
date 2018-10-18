# Generated by Django 2.0 on 2018-10-18 14:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('fundo', '0012_cpr_fundo'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestora',
            name='local',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vertice',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='relacao_ativo', to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vertice',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]

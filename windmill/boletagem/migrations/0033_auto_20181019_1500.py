# Generated by Django 2.0 on 2018-10-19 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('boletagem', '0032_auto_20181019_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='boletapassivo',
            name='boleta_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='boletapassivo',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.ContentType'),
        ),
    ]

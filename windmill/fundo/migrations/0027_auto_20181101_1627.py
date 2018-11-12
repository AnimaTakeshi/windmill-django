# Generated by Django 2.0 on 2018-11-01 19:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('fundo', '0026_auto_20181101_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='carteira',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='carteira',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='carteira',
            name='deletado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='casamentoverticemovimentacao',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='casamentoverticemovimentacao',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='casamentoverticemovimentacao',
            name='deletado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='casamentoverticequantidade',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='casamentoverticequantidade',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='casamentoverticequantidade',
            name='deletado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='certificadopassivo',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='certificadopassivo',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='certificadopassivo',
            name='deletado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cotista',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='cotista',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cotista',
            name='deletado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='movimentacao',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='movimentacao',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movimentacao',
            name='deletado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quantidade',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='quantidade',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='quantidade',
            name='deletado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vertice',
            name='atualizado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='vertice',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='vertice',
            name='deletado_em',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

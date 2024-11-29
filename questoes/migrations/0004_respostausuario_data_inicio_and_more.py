# Generated by Django 5.1.3 on 2024-11-29 19:28

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questoes', '0003_comentarioquestao'),
    ]

    operations = [
        migrations.AddField(
            model_name='respostausuario',
            name='data_inicio',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='respostausuario',
            name='resposta',
            field=models.TextField(),
        ),
    ]

# Generated by Django 5.1.3 on 2024-11-29 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questoes', '0004_respostausuario_data_inicio_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='respostausuario',
            name='data_inicio',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

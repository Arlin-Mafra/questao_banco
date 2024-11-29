# Generated by Django 5.1.3 on 2024-11-29 19:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questoes', '0005_alter_respostausuario_data_inicio'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questao',
            options={'ordering': ['-data_criacao'], 'verbose_name': 'Questão', 'verbose_name_plural': 'Questões'},
        ),
        migrations.RemoveField(
            model_name='questao',
            name='comentarios',
        ),
        migrations.AddField(
            model_name='questao',
            name='dificuldade',
            field=models.CharField(choices=[('F', 'Fácil'), ('M', 'Médio'), ('D', 'Difícil')], default='M', max_length=1),
        ),
        migrations.AlterField(
            model_name='questao',
            name='data_criacao',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='questao',
            name='materia',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questoes.materia'),
        ),
        migrations.AlterField(
            model_name='questao',
            name='tipo_questao',
            field=models.CharField(choices=[('ME', 'Múltipla Escolha'), ('CE', 'Certo ou Errado')], max_length=2),
        ),
    ]
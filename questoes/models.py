from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Materia(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Matéria'
        verbose_name_plural = 'Matérias'

class Questao(models.Model):
    DIFICULDADE_CHOICES = [
        ('F', 'Fácil'),
        ('M', 'Médio'),
        ('D', 'Difícil')
    ]
    
    TIPO_CHOICES = [
        ('ME', 'Múltipla Escolha'),
        ('CE', 'Certo ou Errado'),
    ]
    
    enunciado = models.TextField()
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    tipo_questao = models.CharField(max_length=2, choices=TIPO_CHOICES)
    dificuldade = models.CharField(  # Novo campo
        max_length=1, 
        choices=DIFICULDADE_CHOICES,
        default='M'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Questão {self.id} - {self.materia.nome}"

class QuestaoMultiplaEscolha(models.Model):
    questao = models.OneToOneField(Questao, on_delete=models.CASCADE)
    alternativa_a = models.CharField(max_length=200)
    alternativa_b = models.CharField(max_length=200)
    alternativa_c = models.CharField(max_length=200)
    alternativa_d = models.CharField(max_length=200)
    alternativa_e = models.CharField(max_length=200)
    resposta_correta = models.CharField(max_length=1, verbose_name='Resposta Correta')  # A, B, C, D ou E

    class Meta:
        verbose_name = 'Questão de Múltipla Escolha'
        verbose_name_plural = 'Questões de Múltipla Escolha'

class QuestaoCertoErrado(models.Model):
    questao = models.OneToOneField(Questao, on_delete=models.CASCADE)
    resposta_correta = models.BooleanField(verbose_name='Resposta Correta')

    class Meta:
        verbose_name = 'Questão de Certo ou Errado'
        verbose_name_plural = 'Questões de Certo ou Errado'

class RespostaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    questao = models.ForeignKey('Questao', on_delete=models.CASCADE)
    resposta = models.TextField()
    esta_correta = models.BooleanField()
    data_inicio = models.DateTimeField(default=timezone.now)
    data_resposta = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Resposta do Usuário'
        verbose_name_plural = 'Respostas dos Usuários'
        ordering = ['-data_resposta']
        # Garante que um usuário só tenha uma resposta por questão
        unique_together = ['usuario', 'questao']

    def __str__(self):
        return f"{self.usuario.username} - {self.questao.id}"

class ComentarioQuestao(models.Model):
    questao = models.ForeignKey('Questao', on_delete=models.CASCADE, related_name='comentarios_questao')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'Comentário de {self.usuario.username} em {self.data_criacao}'
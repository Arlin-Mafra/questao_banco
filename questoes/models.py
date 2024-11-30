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
    TIPO_CHOICES = [
        ('ME', 'Múltipla Escolha'),
        ('CE', 'Certo ou Errado')
    ]
    
    DIFICULDADE_CHOICES = [
        ('F', 'Fácil'),
        ('M', 'Médio'),
        ('D', 'Difícil')
    ]
    
    enunciado = models.TextField()
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    tipo_questao = models.CharField(
        max_length=2, 
        choices=TIPO_CHOICES,
        default='ME',  # Definindo Múltipla Escolha como default
        verbose_name='Tipo de Questão'
    )
    dificuldade = models.CharField(
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
    GABARITO_CHOICES = [
        ('A', 'Alternativa A'),
        ('B', 'Alternativa B'),
        ('C', 'Alternativa C'),
        ('D', 'Alternativa D'),
        ('E', 'Alternativa E'),
    ]

    questao = models.OneToOneField(Questao, on_delete=models.CASCADE)
    alternativa_a = models.TextField(max_length=200)
    alternativa_b = models.TextField(max_length=200)
    alternativa_c = models.TextField(max_length=200)
    alternativa_d = models.TextField(max_length=200)
    alternativa_e = models.TextField(max_length=200, blank=True)
    gabarito = models.CharField(max_length=1, choices=GABARITO_CHOICES, default='A')

    def __str__(self):
        return f"Questão ME {self.questao.id}"

class QuestaoCertoErrado(models.Model):
    questao = models.OneToOneField(Questao, on_delete=models.CASCADE)
    gabarito = models.BooleanField(default=False)

    def __str__(self):
        return f"Questão CE {self.questao.id}"

class RespostaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    resposta = models.CharField(max_length=1)  # Para múltipla escolha será A, B, C ou D, para C/E será True/False
    esta_correta = models.BooleanField(default=False)
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['usuario', 'questao']

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
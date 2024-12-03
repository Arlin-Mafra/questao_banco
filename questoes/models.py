from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime

class Materia(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Matéria"
        verbose_name_plural = "Matérias"
        ordering = ['nome']

class Banca(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10, blank=True)
    
    def __str__(self):
        return self.nome if not self.sigla else f"{self.nome} ({self.sigla})"
    
    class Meta:
        verbose_name = "Banca"
        verbose_name_plural = "Bancas"
        ordering = ['nome']

class SubCategoria(models.Model):
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='subcategorias')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.materia.nome} - {self.nome}"
    
    class Meta:
        verbose_name = "Subcategoria"
        verbose_name_plural = "Subcategorias"
        ordering = ['materia__nome', 'nome']

class Questao(models.Model):
    TIPO_QUESTAO_CHOICES = [
        ('ME', 'Múltipla Escolha'),
        ('CE', 'Certo/Errado'),
    ]
    
    DIFICULDADE_CHOICES = [
        ('F', 'Fácil'),
        ('M', 'Médio'),
        ('D', 'Difícil'),
    ]

    enunciado = models.TextField()
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.SET_NULL, null=True, blank=True)
    banca = models.ForeignKey(Banca, on_delete=models.SET_NULL, null=True)
    ano = models.IntegerField(
        validators=[
            MinValueValidator(1990),
            MaxValueValidator(datetime.now().year)
        ]
    )
    tipo_questao = models.CharField(max_length=2, choices=TIPO_QUESTAO_CHOICES, default='ME')
    dificuldade = models.CharField(max_length=1, choices=DIFICULDADE_CHOICES, default='M')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Questão {self.id} - {self.materia}"

    class Meta:
        verbose_name = "Questão"
        verbose_name_plural = "Questões"
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
        return f"ME - Questão {self.questao.id}"

class QuestaoCertoErrado(models.Model):
    questao = models.OneToOneField(Questao, on_delete=models.CASCADE)
    gabarito = models.BooleanField(default=False)

    def __str__(self):
        return f"CE - Questão {self.questao.id}"

class RespostaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    resposta = models.CharField(max_length=1)  # Para múltipla escolha será A, B, C ou D, para C/E será True/False
    esta_correta = models.BooleanField(default=False)
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['usuario', 'questao']
        ordering = ['-data_resposta']

class ComentarioQuestao(models.Model):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ['-data_criacao']
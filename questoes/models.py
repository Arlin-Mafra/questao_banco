from django.db import models
from django.contrib.auth import get_user_model

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
    TIPOS_QUESTAO = [
        ('ME', 'Múltipla Escolha'),
        ('CE', 'Certo ou Errado'),
    ]

    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, verbose_name='Matéria')
    tipo_questao = models.CharField(max_length=2, choices=TIPOS_QUESTAO, verbose_name='Tipo de Questão')
    enunciado = models.TextField()
    comentarios = models.TextField(blank=True, verbose_name='Comentários')
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

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
    resposta = models.CharField(max_length=10)  # Armazena 'A', 'B', 'C', 'D', 'E' ou 'True'/'False'
    esta_correta = models.BooleanField()
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Resposta do Usuário'
        verbose_name_plural = 'Respostas dos Usuários'
        ordering = ['-data_resposta']
        # Garante que um usuário só tenha uma resposta por questão
        unique_together = ['usuario', 'questao']

    def __str__(self):
        return f"{self.usuario.username} - Questão {self.questao.id} - {'Correta' if self.esta_correta else 'Incorreta'}"

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
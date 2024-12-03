from django.contrib import admin
from .models import (
    Materia, Banca, SubCategoria, Questao, 
    QuestaoMultiplaEscolha, QuestaoCertoErrado,
    RespostaUsuario, ComentarioQuestao
)

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Banca)
class BancaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla')
    search_fields = ('nome', 'sigla')

@admin.register(SubCategoria)
class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'materia')
    list_filter = ('materia',)
    search_fields = ('nome', 'materia__nome')

@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'materia', 'subcategoria', 'banca', 'ano', 'tipo_questao', 'dificuldade')
    list_filter = ('materia', 'banca', 'tipo_questao', 'dificuldade')
    search_fields = ('enunciado',)

@admin.register(QuestaoMultiplaEscolha)
class QuestaoMultiplaEscolhaAdmin(admin.ModelAdmin):
    list_display = ('questao', 'gabarito')
    list_filter = ('gabarito',)

@admin.register(QuestaoCertoErrado)
class QuestaoCertoErradoAdmin(admin.ModelAdmin):
    list_display = ('questao', 'gabarito')
    list_filter = ('gabarito',)

@admin.register(RespostaUsuario)
class RespostaUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'questao', 'resposta', 'esta_correta', 'data_resposta')
    list_filter = ('usuario', 'questao', 'esta_correta')
    search_fields = ('resposta',)

@admin.register(ComentarioQuestao)
class ComentarioQuestaoAdmin(admin.ModelAdmin):
    list_display = ('questao', 'usuario', 'texto', 'data_criacao')
    list_filter = ('questao', 'usuario')
    search_fields = ('texto',)

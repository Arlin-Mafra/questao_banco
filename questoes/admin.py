from django.contrib import admin
from .models import Materia, Questao, QuestaoMultiplaEscolha, QuestaoCertoErrado

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)

@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ('enunciado', 'materia', 'tipo_questao', 'data_criacao')
    list_filter = ('materia', 'tipo_questao')
    search_fields = ('enunciado',)

@admin.register(QuestaoMultiplaEscolha)
class QuestaoMultiplaEscolhaAdmin(admin.ModelAdmin):
    list_display = ('questao', 'resposta_correta')
    list_filter = ('resposta_correta',)

@admin.register(QuestaoCertoErrado)
class QuestaoCertoErradoAdmin(admin.ModelAdmin):
    list_display = ('questao', 'resposta_correta')
    list_filter = ('resposta_correta',)

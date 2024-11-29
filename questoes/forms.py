from django import forms
from .models import Questao, QuestaoMultiplaEscolha, QuestaoCertoErrado, Materia

class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = ['materia', 'tipo_questao', 'enunciado', 'comentarios']

class QuestaoMultiplaEscolhaForm(forms.ModelForm):
    class Meta:
        model = QuestaoMultiplaEscolha
        fields = ['alternativa_a', 'alternativa_b', 'alternativa_c', 
                 'alternativa_d', 'alternativa_e', 'resposta_correta']

class QuestaoCertoErradoForm(forms.ModelForm):
    class Meta:
        model = QuestaoCertoErrado
        fields = ['resposta_correta']
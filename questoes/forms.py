from django import forms
from .models import Questao, QuestaoMultiplaEscolha, QuestaoCertoErrado

class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = ['enunciado', 'materia', 'tipo_questao', 'dificuldade']
        widgets = {
            'enunciado': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Digite o enunciado da questão'
            }),
            'materia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_questao': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'dificuldade': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            })
        }

class QuestaoMultiplaEscolhaForm(forms.ModelForm):
    class Meta:
        model = QuestaoMultiplaEscolha
        fields = ['alternativa_a', 'alternativa_b', 'alternativa_c', 'alternativa_d', 'alternativa_e', 'gabarito']
        widgets = {
            'alternativa_a': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Digite a alternativa A'
            }),
            'alternativa_b': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Digite a alternativa B'
            }),
            'alternativa_c': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Digite a alternativa C'
            }),
            'alternativa_d': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Digite a alternativa D'
            }),
            'alternativa_e': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Digite a alternativa E'
            }),
            'gabarito': forms.Select(attrs={'class': 'form-select'})
        }

class QuestaoCertoErradoForm(forms.ModelForm):
    GABARITO_CHOICES = (
        ('True', 'Certo'),
        ('False', 'Errado')
    )

    gabarito = forms.TypedChoiceField(
        choices=GABARITO_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
            'required': 'required'
        }),
        coerce=lambda x: x == 'True',
        required=True,
        label='Gabarito',
        error_messages={
            'required': 'Por favor, selecione se a resposta é Certo ou Errado.'
        }
    )

    class Meta:
        model = QuestaoCertoErrado
        fields = ['gabarito']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gabarito'].required = True
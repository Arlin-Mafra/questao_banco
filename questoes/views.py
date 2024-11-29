from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import QuestaoForm, QuestaoMultiplaEscolhaForm, QuestaoCertoErradoForm
from .models import Questao, Materia, QuestaoMultiplaEscolha, QuestaoCertoErrado, RespostaUsuario, ComentarioQuestao
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string

def criar_questao(request):
    if request.method == 'POST':
        questao_form = QuestaoForm(request.POST)
        if questao_form.is_valid():
            questao = questao_form.save()
            
            if questao.tipo_questao == 'ME':
                me_form = QuestaoMultiplaEscolhaForm(request.POST)
                if me_form.is_valid():
                    questao_me = me_form.save(commit=False)
                    questao_me.questao = questao
                    questao_me.save()
            else:
                ce_form = QuestaoCertoErradoForm(request.POST)
                if ce_form.is_valid():
                    questao_ce = ce_form.save(commit=False)
                    questao_ce.questao = questao
                    questao_ce.save()
                    
            return redirect('lista_questoes')
    else:
        questao_form = QuestaoForm()
        me_form = QuestaoMultiplaEscolhaForm()
        ce_form = QuestaoCertoErradoForm()
    
    return render(request, 'questoes/criar_questao.html', {
        'questao_form': questao_form,
        'me_form': me_form,
        'ce_form': ce_form,
    })

class MateriaListView(ListView):
    model = Materia
    template_name = 'questoes/materia/lista_materias.html'
    context_object_name = 'materias'
    ordering = ['nome']

class MateriaCriarView(SuccessMessageMixin, CreateView):
    model = Materia
    template_name = 'questoes/materia/form_materia.html'
    fields = ['nome', 'descricao']
    success_url = reverse_lazy('lista_materias')
    success_message = "Matéria '%(nome)s' foi criada com sucesso!"

class MateriaEditarView(SuccessMessageMixin, UpdateView):
    model = Materia
    template_name = 'questoes/materia/form_materia.html'
    fields = ['nome', 'descricao']
    success_url = reverse_lazy('lista_materias')
    success_message = "Matéria '%(nome)s' foi atualizada com sucesso!"

class MateriaDeletarView(SuccessMessageMixin, DeleteView):
    model = Materia
    template_name = 'questoes/materia/confirmar_delete_materia.html'
    success_url = reverse_lazy('lista_materias')
    success_message = "Matéria excluída com sucesso!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MateriaDeletarView, self).delete(request, *args, **kwargs)

@login_required
def responder_questoes(request):
    materias = Materia.objects.all()
    materia_id = request.GET.get('materia')
    
    questoes = Questao.objects.select_related(
        'materia',
        'questaomultiplaescolha',
        'questaocertoerrado'
    ).order_by('materia__nome', 'id')

    if materia_id:
        questoes = questoes.filter(materia_id=materia_id)

    # Pegar respostas anteriores do usuário
    respostas_anteriores = RespostaUsuario.objects.filter(
        usuario=request.user,
        questao__in=questoes
    ).select_related('questao')
    
    # Criar dicionários para armazenar respostas e status anteriores
    respostas_usuario = {r.questao.id: r.resposta for r in respostas_anteriores}
    status_questoes = {r.questao.id: 'correta' if r.esta_correta else 'incorreta' 
                      for r in respostas_anteriores}

    paginator = Paginator(questoes, request.GET.get('paginate_by', 5))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        for questao in page_obj:
            resposta_usuario = request.POST.get(f'resposta_{questao.id}')
            if not resposta_usuario:
                continue

            esta_correta = False
            if questao.tipo_questao == 'ME':
                mc = questao.questaomultiplaescolha
                esta_correta = mc and resposta_usuario == mc.resposta_correta
            elif questao.tipo_questao == 'CE':
                ce = questao.questaocertoerrado
                esta_correta = ce and resposta_usuario == str(ce.resposta_correta)

            # Salvar ou atualizar a resposta do usuário
            RespostaUsuario.objects.update_or_create(
                usuario=request.user,
                questao=questao,
                defaults={
                    'resposta': resposta_usuario,
                    'esta_correta': esta_correta
                }
            )

            # Atualizar dicionários para feedback imediato
            respostas_usuario[questao.id] = resposta_usuario
            status_questoes[questao.id] = 'correta' if esta_correta else 'incorreta'

            if esta_correta:
                messages.success(request, f'Questão {questao.id}: Resposta correta!')
            else:
                if questao.tipo_questao == 'ME':
                    messages.error(request, f'Questão {questao.id}: Resposta incorreta. A correta é {mc.resposta_correta}.')
                else:
                    messages.error(request, f'Questão {questao.id}: Resposta incorreta. A correta é {"Verdadeiro" if ce.resposta_correta else "Falso"}.')

    # Adicionar estatísticas do usuário
    total_respondidas = RespostaUsuario.objects.filter(usuario=request.user).count()
    total_corretas = RespostaUsuario.objects.filter(usuario=request.user, esta_correta=True).count()
    
    return render(request, 'questoes/responder_questoes.html', {
        'materias': materias,
        'page_obj': page_obj,
        'materia_id': materia_id,
        'respostas_usuario': respostas_usuario,
        'status_questoes': status_questoes,
        'estatisticas': {
            'total_respondidas': total_respondidas,
            'total_corretas': total_corretas,
            'percentual_acerto': (total_corretas / total_respondidas * 100) if total_respondidas > 0 else 0
        }
    })

@login_required
def adicionar_comentario(request, questao_id):
    if request.method == 'POST':
        texto = request.POST.get('comentario')
        if texto:
            try:
                comentario = ComentarioQuestao.objects.create(
                    questao_id=questao_id,
                    usuario=request.user,
                    texto=texto
                )
                
                html = render_to_string('questoes/includes/comentario.html', 
                                      {'comentario': comentario},
                                      request=request)
                
                return JsonResponse({
                    'status': 'success',
                    'html': html,
                    'message': 'Comentário adicionado com sucesso!'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao adicionar comentário: {str(e)}'
                })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'O texto do comentário não pode estar vazio.'
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método não permitido.'
    })

@login_required
def deletar_comentario(request, comentario_id):
    if not request.user.is_superuser:
        return JsonResponse({
            'status': 'error',
            'message': 'Você não tem permissão para deletar comentários.'
        })
    
    try:
        comentario = ComentarioQuestao.objects.get(id=comentario_id)
        questao_id = comentario.questao.id
        comentario.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Comentário deletado com sucesso!',
            'questao_id': questao_id
        })
    except ComentarioQuestao.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Comentário não encontrado.'
        })
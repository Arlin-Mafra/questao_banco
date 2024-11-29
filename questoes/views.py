from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import QuestaoForm, QuestaoMultiplaEscolhaForm, QuestaoCertoErradoForm
from .models import Questao, Materia, QuestaoMultiplaEscolha, QuestaoCertoErrado
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch

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

def responder_questoes(request):
    materias = Materia.objects.all()
    materia_id = request.GET.get('materia')
    
    questoes = Questao.objects.select_related(
        'materia',
        'questaomultiplaescolha',
        'questaocertoerrado'
    )

    if materia_id:
        questoes = questoes.filter(materia_id=materia_id)

    paginator = Paginator(questoes, request.GET.get('paginate_by', 5))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Dicionários para armazenar as respostas e status
    respostas_usuario = {}
    status_questoes = {}

    if request.method == 'POST':
        for questao in page_obj:
            resposta_usuario = request.POST.get(f'resposta_{questao.id}')
            respostas_usuario[questao.id] = resposta_usuario
            
            if questao.tipo_questao == 'ME':
                mc = questao.questaomultiplaescolha
                if mc and resposta_usuario == mc.resposta_correta:
                    status_questoes[questao.id] = 'correta'
                    messages.success(request, f'Questão {questao.id}: Resposta correta!')
                else:
                    status_questoes[questao.id] = 'incorreta'
                    messages.error(request, f'Questão {questao.id}: Resposta incorreta. A correta é {mc.resposta_correta if mc else "N/A"}.')
            elif questao.tipo_questao == 'CE':
                ce = questao.questaocertoerrado
                if ce and resposta_usuario == str(ce.resposta_correta):
                    status_questoes[questao.id] = 'correta'
                    messages.success(request, f'Questão {questao.id}: Resposta correta!')
                else:
                    status_questoes[questao.id] = 'incorreta'
                    messages.error(request, f'Questão {questao.id}: Resposta incorreta. A correta é {"Verdadeiro" if ce and ce.resposta_correta else "Falso"}.')

    return render(request, 'questoes/responder_questoes.html', {
        'materias': materias,
        'page_obj': page_obj,
        'materia_id': materia_id,
        'respostas_usuario': respostas_usuario,
        'status_questoes': status_questoes,
    })
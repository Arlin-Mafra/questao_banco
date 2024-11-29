from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import QuestaoForm, QuestaoMultiplaEscolhaForm, QuestaoCertoErradoForm
from .models import Questao, Materia, RespostaUsuario, ComentarioQuestao
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Count, Avg
from django.db.models import Q
from django.db.models import Case
from django.db.models import When
from django.db.models import FloatField
from django.db.models.functions import TruncDay, ExtractHour
from datetime import datetime, timedelta
from django.db.models import F
from django.utils import timezone

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

# View para página inicial
@login_required
def home(request):
    return redirect('dashboard')

# View para registro de usuários
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada com sucesso para {username}!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'questoes/registro.html', {'form': form})

@login_required
def dashboard(request):
    # Estatísticas gerais
    total_questoes = Questao.objects.count()
    total_usuarios = User.objects.count()
    total_materias = Materia.objects.count()
    
    # Estatísticas do usuário
    questoes_respondidas = RespostaUsuario.objects.filter(usuario=request.user).count()
    questoes_corretas = RespostaUsuario.objects.filter(
        usuario=request.user, 
        esta_correta=True
    ).count()
    
    # Calcular porcentagem de acertos
    taxa_acerto = (questoes_corretas / questoes_respondidas * 100) if questoes_respondidas > 0 else 0
    
    # Estatísticas por matéria
    desempenho_por_materia = RespostaUsuario.objects.filter(
        usuario=request.user
    ).values(
        'questao__materia__nome'
    ).annotate(
        total=Count('id'),
        corretas=Count('id', filter=Q(esta_correta=True)),
        taxa_acerto=Avg(Case(
            When(esta_correta=True, then=100),
            When(esta_correta=False, then=0),
            output_field=FloatField(),
        ))
    ).order_by('-taxa_acerto')
    
    # Últimas questões respondidas
    ultimas_respostas = RespostaUsuario.objects.filter(
        usuario=request.user
    ).select_related('questao').order_by('-data_resposta')[:5]
    
    # Ranking de usuários (top 5)
    ranking_usuarios = User.objects.annotate(
        total_corretas=Count('respostausuario', filter=Q(respostausuario__esta_correta=True))
    ).order_by('-total_corretas')[:5]
    
    context = {
        'total_questoes': total_questoes,
        'total_usuarios': total_usuarios,
        'total_materias': total_materias,
        'questoes_respondidas': questoes_respondidas,
        'questoes_corretas': questoes_corretas,
        'taxa_acerto': round(taxa_acerto, 1),
        'desempenho_por_materia': desempenho_por_materia,
        'ultimas_respostas': ultimas_respostas,
        'ranking_usuarios': ranking_usuarios,
    }
    
    return render(request, 'questoes/dashboard.html', context)

@login_required
def relatorios(request):
    # Período selecionado (default: último mês)
    periodo = request.GET.get('periodo', '30')  # dias
    data_inicio = timezone.now() - timedelta(days=int(periodo))
    
    # Evolução diária
    evolucao_diaria = RespostaUsuario.objects.filter(
        usuario=request.user,
        data_resposta__gte=data_inicio
    ).annotate(
        dia=TruncDay('data_resposta', tzinfo=timezone.get_current_timezone())
    ).values('dia').annotate(
        total=Count('id'),
        corretas=Count('id', filter=Q(esta_correta=True)),
        taxa_acerto=Avg(Case(
            When(esta_correta=True, then=100),
            When(esta_correta=False, then=0),
            output_field=FloatField(),
        ))
    ).order_by('dia')
    
    # Horários mais produtivos
    horarios_produtivos = RespostaUsuario.objects.filter(
        usuario=request.user,
        esta_correta=True
    ).annotate(
        hora=ExtractHour('data_resposta', tzinfo=timezone.get_current_timezone())
    ).values('hora').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    # Análise por dificuldade
    analise_dificuldade = RespostaUsuario.objects.filter(
        usuario=request.user
    ).values(
        'questao__dificuldade'
    ).annotate(
        total=Count('id'),
        corretas=Count('id', filter=Q(esta_correta=True)),
        taxa_acerto=Avg(Case(
            When(esta_correta=True, then=100),
            When(esta_correta=False, then=0),
            output_field=FloatField(),
        ))
    ).order_by('questao__dificuldade')
    
    # Converter códigos de dificuldade para labels legíveis
    dificuldade_map = dict(Questao.DIFICULDADE_CHOICES)
    dificuldade_labels = [dificuldade_map[item['questao__dificuldade']] 
                         for item in analise_dificuldade]
    dificuldade_data = [float(item['taxa_acerto'] or 0) 
                       for item in analise_dificuldade]
    
    # Comparação com média geral
    comparacao_geral = []
    for materia in Materia.objects.all():
        media_geral = RespostaUsuario.objects.filter(
            questao__materia=materia
        ).aggregate(
            taxa=Avg(Case(
                When(esta_correta=True, then=100),
                When(esta_correta=False, then=0),
                output_field=FloatField(),
            ))
        )['taxa'] or 0
        
        media_usuario = RespostaUsuario.objects.filter(
            questao__materia=materia,
            usuario=request.user
        ).aggregate(
            taxa=Avg(Case(
                When(esta_correta=True, then=100),
                When(esta_correta=False, then=0),
                output_field=FloatField(),
            ))
        )['taxa'] or 0
        
        comparacao_geral.append({
            'materia': materia.nome,
            'media_geral': round(media_geral, 1),
            'media_usuario': round(media_usuario, 1)
        })

    # Preparar dados para os gráficos
    evolucao_diaria_labels = [item['dia'].strftime('%d/%m') for item in evolucao_diaria]
    evolucao_diaria_data = [float(item['taxa_acerto'] or 0) for item in evolucao_diaria]
    
    context = {
        'evolucao_diaria': evolucao_diaria,
        'horarios_produtivos': horarios_produtivos,
        'analise_dificuldade': analise_dificuldade,
        'comparacao_geral': comparacao_geral,
        'periodo_selecionado': periodo,
        'evolucao_diaria_labels': evolucao_diaria_labels,
        'evolucao_diaria_data': evolucao_diaria_data,
        'dificuldade_labels': dificuldade_labels,
        'dificuldade_data': dificuldade_data,
    }
    
    return render(request, 'questoes/relatorios.html', context)
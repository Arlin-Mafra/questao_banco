from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import QuestaoForm, QuestaoMultiplaEscolhaForm, QuestaoCertoErradoForm
from .models import Questao, Materia, RespostaUsuario, ComentarioQuestao, SubCategoria, Banca
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
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from urllib.parse import urlencode

def criar_questao(request):
    if request.method == 'POST':
        print("POST data:", request.POST)  # Debug completo do POST
        questao_form = QuestaoForm(request.POST)
        tipo_questao = request.POST.get('tipo_questao')
        me_form = None
        ce_form = None
        
        if tipo_questao == 'CE':
            ce_form = QuestaoCertoErradoForm(request.POST)
            print("CE Form data:", ce_form.data)
            print("CE Form is bound:", ce_form.is_bound)
            print("Gabarito value:", request.POST.get('gabarito'))
            print("CE Form fields:", ce_form.fields['gabarito'])
            if not ce_form.is_valid():
                print("CE Form errors:", ce_form.errors)
        else:
            me_form = QuestaoMultiplaEscolhaForm(request.POST)
        
        try:
            with transaction.atomic():
                if questao_form.is_valid():
                    questao = questao_form.save()
                    
                    if tipo_questao == 'ME':
                        if me_form.is_valid():
                            questao_me = me_form.save(commit=False)
                            questao_me.questao = questao
                            questao_me.save()
                            messages.success(request, 'Questão de múltipla escolha criada com sucesso!')
                            return redirect('criar_questao')
                        else:
                            raise ValueError('Formulário de múltipla escolha inválido')
                    
                    elif tipo_questao == 'CE':
                        if ce_form.is_valid():
                            questao_ce = ce_form.save(commit=False)
                            questao_ce.questao = questao
                            questao_ce.save()  # O gabarito já foi convertido no clean_gabarito
                            messages.success(request, 'Questão de certo/errado criada com sucesso!')
                            return redirect('criar_questao')
                        else:
                            print("Erros do formulário CE:", ce_form.errors)  # Debug
                            raise ValueError('Formulário de certo/errado inválido')
                    
                    else:
                        raise ValueError('Tipo de questão inválido')
                else:
                    messages.error(request, 'Erro ao criar questão. Verifique os campos.', extra_tags='danger')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erro ao criar questão: {str(e)}')
    else:
        questao_form = QuestaoForm()
        me_form = QuestaoMultiplaEscolhaForm()
        ce_form = QuestaoCertoErradoForm()
    
    return render(request, 'questoes/criar_questao.html', {
        'questao_form': questao_form,
        'me_form': me_form,
        'ce_form': ce_form,
    })

class MateriaListView(LoginRequiredMixin, ListView):
    model = Materia
    template_name = 'questoes/materia/lista_materias.html'
    context_object_name = 'materias'

class MateriaCreateView(LoginRequiredMixin, CreateView):
    model = Materia
    template_name = 'questoes/materia/form_materia.html'
    fields = ['nome', 'descricao']
    success_url = reverse_lazy('materias')

class MateriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Materia
    template_name = 'questoes/materia/form_materia.html'
    fields = ['nome', 'descricao']
    success_url = reverse_lazy('materias')

class MateriaDeleteView(LoginRequiredMixin, DeleteView):
    model = Materia
    template_name = 'questoes/materia/confirmar_delete_materia.html'
    success_url = reverse_lazy('materias')

class SubCategoriaListView(LoginRequiredMixin, ListView):
    model = SubCategoria
    template_name = 'questoes/subcategoria/lista_subcategorias.html'
    context_object_name = 'subcategorias'

class SubCategoriaCreateView(LoginRequiredMixin, CreateView):
    model = SubCategoria
    template_name = 'questoes/subcategoria/form_subcategoria.html'
    fields = ['materia', 'nome', 'descricao']
    success_url = reverse_lazy('subcategorias')

class SubCategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = SubCategoria
    template_name = 'questoes/subcategoria/form_subcategoria.html'
    fields = ['materia', 'nome', 'descricao']
    success_url = reverse_lazy('subcategorias')

class SubCategoriaDeleteView(LoginRequiredMixin, DeleteView):
    model = SubCategoria
    template_name = 'questoes/subcategoria/confirmar_delete_subcategoria.html'
    success_url = reverse_lazy('subcategorias')

class BancaListView(LoginRequiredMixin, ListView):
    model = Banca
    template_name = 'questoes/banca/lista_bancas.html'
    context_object_name = 'bancas'

class BancaCreateView(LoginRequiredMixin, CreateView):
    model = Banca
    template_name = 'questoes/banca/form_banca.html'
    fields = ['nome', 'sigla']
    success_url = reverse_lazy('bancas')

class BancaUpdateView(LoginRequiredMixin, UpdateView):
    model = Banca
    template_name = 'questoes/banca/form_banca.html'
    fields = ['nome', 'sigla']
    success_url = reverse_lazy('bancas')

class BancaDeleteView(LoginRequiredMixin, DeleteView):
    model = Banca
    template_name = 'questoes/banca/confirmar_delete_banca.html'
    success_url = reverse_lazy('bancas')

@login_required
def responder_questoes(request):
    materia_id = request.GET.get('materia')
    mostrar_respondidas = request.GET.get('mostrar_respondidas', 'nao') == 'sim'
    
    # Pegar todas as matérias para o dropdown
    materias = Materia.objects.all()
    
    # Iniciar queryset base
    questoes = Questao.objects.all()
    
    # Filtrar por matéria se selecionado
    if materia_id:
        questoes = questoes.filter(materia_id=materia_id)
    
    # Filtrar questões não respondidas, se necessário
    if not mostrar_respondidas:
        questoes_respondidas = RespostaUsuario.objects.filter(
            usuario=request.user
        ).values_list('questao_id', flat=True)
        questoes = questoes.exclude(id__in=questoes_respondidas)
    
    questoes = questoes.order_by('?')
    
    # Paginação
    paginator = Paginator(questoes, 1)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Processar respostas se for POST
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('resposta_'):
                questao_id = key.split('_')[1]
                try:
                    questao = Questao.objects.get(id=questao_id)
                    
                    # Verificar se a resposta está correta
                    if questao.tipo_questao == 'ME':
                        esta_correta = (value == questao.questaomultiplaescolha.gabarito)
                    else:
                        resposta_usuario = value.lower() == 'true'
                        esta_correta = (resposta_usuario == questao.questaocertoerrado.gabarito)
                    
                    # Deletar resposta anterior se existir
                    RespostaUsuario.objects.filter(
                        usuario=request.user,
                        questao=questao
                    ).delete()
                    
                    # Criar nova resposta
                    RespostaUsuario.objects.create(
                        usuario=request.user,
                        questao=questao,
                        resposta=value,
                        esta_correta=esta_correta
                    )
                    
                    # Atualizar a questão atual com o feedback
                    if page_obj:
                        questao_atual = page_obj[0]
                        questao_atual.respondida = True
                        questao_atual.resposta_usuario = value
                        questao_atual.status = 'correta' if esta_correta else 'incorreta'
                    
                except Questao.DoesNotExist:
                    continue
    
    # Preparar dados para o template
    if page_obj:
        questao_atual = page_obj[0]
        resposta = RespostaUsuario.objects.filter(
            usuario=request.user,
            questao=questao_atual
        ).first()
        
        if resposta:
            questao_atual.respondida = True
            questao_atual.resposta_usuario = resposta.resposta
            questao_atual.status = 'correta' if resposta.esta_correta else 'incorreta'
        else:
            questao_atual.respondida = False
    
    # Calcular estatísticas
    total_respondidas = RespostaUsuario.objects.filter(usuario=request.user).count()
    total_corretas = RespostaUsuario.objects.filter(usuario=request.user, esta_correta=True).count()
    percentual_acerto = (total_corretas / total_respondidas * 100) if total_respondidas > 0 else 0
    
    context = {
        'page_obj': page_obj,
        'materias': materias,
        'materia_id': materia_id,
        'mostrar_respondidas': mostrar_respondidas,
        'estatisticas': {
            'total_respondidas': total_respondidas,
            'total_corretas': total_corretas,
            'percentual_acerto': percentual_acerto
        }
    }
    
    return render(request, 'questoes/responder_questoes.html', context)

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
    
    # Converter códigos de dificuldade para labels legveis
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

def get_subcategorias(request, materia_id):
    # Usando distinct() simples e ordenando por nome
    subcategorias = (
        SubCategoria.objects
        .filter(materia_id=materia_id)
        .values('id', 'nome')
        .distinct()
        .order_by('nome')
    )
    print(subcategorias)
    return JsonResponse(list(subcategorias), safe=False)
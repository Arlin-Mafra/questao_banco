from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # URLs de Autenticação
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='questoes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('registro/', views.registro, name='registro'),
    
    # URLs de Questões
    path('criar_questao/', views.criar_questao, name='criar_questao'),
    path('responder_questoes/', views.responder_questoes, name='responder_questoes'),
    path('adicionar_comentario/<int:questao_id>/', views.adicionar_comentario, name='adicionar_comentario'),
    path('deletar_comentario/<int:comentario_id>/', views.deletar_comentario, name='deletar_comentario'),
    
    # URLs de Matéria
    path('materias/', views.MateriaListView.as_view(), name='lista_materias'),
    path('materias/criar/', views.MateriaCriarView.as_view(), name='criar_materia'),
    path('materias/<int:pk>/editar/', views.MateriaEditarView.as_view(), name='editar_materia'),
    path('materias/<int:pk>/deletar/', views.MateriaDeletarView.as_view(), name='deletar_materia'),
    
    # URLs de Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('relatorios/', views.relatorios, name='relatorios'),
]

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
    # path('historico/', views.historico, name='historico'),
    
    # URLs de Matéria
    path('materias/', views.MateriaListView.as_view(), name='materias'),
    path('materias/criar/', views.MateriaCreateView.as_view(), name='criar_materia'),
    path('materias/<int:pk>/editar/', views.MateriaUpdateView.as_view(), name='editar_materia'),
    path('materias/<int:pk>/excluir/', views.MateriaDeleteView.as_view(), name='excluir_materia'),
    
    # URLs de SubCategoria
    path('subcategorias/', views.SubCategoriaListView.as_view(), name='subcategorias'),
    path('subcategorias/criar/', views.SubCategoriaCreateView.as_view(), name='criar_subcategoria'),
    path('subcategorias/<int:pk>/editar/', views.SubCategoriaUpdateView.as_view(), name='editar_subcategoria'),
    path('subcategorias/<int:pk>/excluir/', views.SubCategoriaDeleteView.as_view(), name='excluir_subcategoria'),
    
    # URLs de Banca
    path('bancas/', views.BancaListView.as_view(), name='bancas'),
    path('bancas/criar/', views.BancaCreateView.as_view(), name='criar_banca'),
    path('bancas/<int:pk>/editar/', views.BancaUpdateView.as_view(), name='editar_banca'),
    path('bancas/<int:pk>/excluir/', views.BancaDeleteView.as_view(), name='excluir_banca'),
    
    # URLs de Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('get_subcategorias/<int:materia_id>/', views.get_subcategorias, name='get_subcategorias'),
]

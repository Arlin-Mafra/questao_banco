from django.urls import path
from . import views

urlpatterns = [
    path('criar/', views.criar_questao, name='criar_questao'),
    # URLs para Matérias
    path('materias/', views.MateriaListView.as_view(), name='lista_materias'),
    path('materias/criar/', views.MateriaCriarView.as_view(), name='criar_materia'),
    path('materias/<int:pk>/editar/', views.MateriaEditarView.as_view(), name='editar_materia'),
    path('materias/<int:pk>/deletar/', views.MateriaDeletarView.as_view(), name='deletar_materia'),
    path('questoes/', views.responder_questoes, name='responder_questoes'),
]

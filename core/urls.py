from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
urlpatterns=[
path('',views.home,name='home'),path('sobre/',views.sobre,name='sobre'),path('cursos/',views.cursos,name='cursos'),path('cursos/<int:pk>/',views.curso_detalhe,name='curso_detalhe'),path('eventos/',views.eventos,name='eventos'),path('galeria/',views.galeria,name='galeria'),path('equipe/',views.equipe,name='equipe'),
path('login/',views.LoginView.as_view(template_name='core/login.html'),name='login'),path('sair/',LogoutView.as_view(),name='logout'),path('painel/',views.painel,name='painel'),
]
for base,classes in [('aluno',(views.AlunoList,views.AlunoCreate,views.AlunoUpdate,views.AlunoDelete)),('instrutor',(views.InstrutorList,views.InstrutorCreate,views.InstrutorUpdate,views.InstrutorDelete)),('curso',(views.CursoList,views.CursoCreate,views.CursoUpdate,views.CursoDelete)),('evento',(views.EventoList,views.EventoCreate,views.EventoUpdate,views.EventoDelete))]:
    L,C,U,D=classes; urlpatterns += [path(f'painel/{base}s/',L.as_view(),name=f'{base}_lista'),path(f'painel/{base}s/novo/',C.as_view(),name=f'{base}_novo'),path(f'painel/{base}s/<int:pk>/editar/',U.as_view(),name=f'{base}_editar'),path(f'painel/{base}s/<int:pk>/excluir/',D.as_view(),name=f'{base}_excluir')]
urlpatterns += [
path('painel/matriculas/',views.MatriculaList.as_view(),name='matricula_lista'),path('painel/matriculas/nova/',views.MatriculaCreate.as_view(),name='matricula_novo'),path('painel/matriculas/<int:pk>/editar/',views.MatriculaUpdate.as_view(),name='matricula_editar'),path('painel/matriculas/<int:pk>/excluir/',views.MatriculaDelete.as_view(),name='matricula_excluir'),
path('painel/aulas/',views.AulaList.as_view(),name='aula_lista'),path('painel/aulas/nova/',views.AulaCreate.as_view(),name='aula_novo'),path('painel/aulas/<int:pk>/editar/',views.AulaUpdate.as_view(),name='aula_editar'),path('painel/aulas/<int:pk>/excluir/',views.AulaDelete.as_view(),name='aula_excluir'),path('painel/aulas/<int:pk>/chamada/',views.chamada,name='chamada')]

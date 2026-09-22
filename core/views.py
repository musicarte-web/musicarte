from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import *
from .forms import *

def home(request):
    return render(request,'core/home.html',{'cursos':Curso.objects.filter(ativo=True)[:6],'eventos':Evento.objects.filter(publicado=True)[:3],'midias':Midia.objects.filter(publicada=True)[:6]})
def sobre(request): return render(request,'core/sobre.html')
def cursos(request): return render(request,'core/cursos.html',{'cursos':Curso.objects.filter(ativo=True)})
def curso_detalhe(request,pk): return render(request,'core/curso_detalhe.html',{'curso':get_object_or_404(Curso,pk=pk,ativo=True)})
def eventos(request): return render(request,'core/eventos.html',{'eventos':Evento.objects.filter(publicado=True)})
def galeria(request): return render(request,'core/galeria.html',{'midias':Midia.objects.filter(publicada=True)})
def equipe(request): return render(request,'core/equipe.html',{'instrutores':Instrutor.objects.filter(ativo=True)})

@login_required
def painel(request):
    return render(request,'core/painel.html',{'alunos':Aluno.objects.count(),'instrutores':Instrutor.objects.count(),'cursos':Curso.objects.count(),'matriculas':Matricula.objects.filter(status='ATIVA').count(),'aulas':Aula.objects.count(),'eventos':Evento.objects.count()})

class SearchList(LoginRequiredMixin,ListView):
    paginate_by=10
    search_fields=[]
    def get_queryset(self):
        qs=super().get_queryset(); q=self.request.GET.get('q','').strip()
        if q and self.search_fields:
            query=Q()
            for field in self.search_fields: query |= Q(**{f'{field}__icontains':q})
            qs=qs.filter(query)
        return qs
class MsgMixin:
    success_url=reverse_lazy('painel')
    def form_valid(self,form):
        messages.success(self.request,'Registro salvo com sucesso.')
        return super().form_valid(form)
    def delete(self,*args,**kwargs):
        messages.success(self.request,'Registro excluído com sucesso.')
        return super().delete(*args,**kwargs)

def crud(model,form,prefix,fields):
    return (
        type(prefix+'List',(SearchList,),{'model':model,'template_name':'core/crud_list.html','extra_context':{'titulo':prefix,'novo_url':f'{prefix.lower()}_novo','editar_url':f'{prefix.lower()}_editar','excluir_url':f'{prefix.lower()}_excluir','colunas':fields},'search_fields':['nome'] if hasattr(model,'nome') else ['titulo'] if hasattr(model,'titulo') else []}),
        type(prefix+'Create',(LoginRequiredMixin,MsgMixin,CreateView),{'model':model,'form_class':form,'template_name':'core/form.html','success_url':reverse_lazy(f'{prefix.lower()}_lista'),'extra_context':{'titulo':f'Novo {prefix}'}}),
        type(prefix+'Update',(LoginRequiredMixin,MsgMixin,UpdateView),{'model':model,'form_class':form,'template_name':'core/form.html','success_url':reverse_lazy(f'{prefix.lower()}_lista'),'extra_context':{'titulo':f'Editar {prefix}'}}),
        type(prefix+'Delete',(LoginRequiredMixin,DeleteView),{'model':model,'template_name':'core/confirm_delete.html','success_url':reverse_lazy(f'{prefix.lower()}_lista'),'extra_context':{'titulo':f'Excluir {prefix}'}})
    )
AlunoList,AlunoCreate,AlunoUpdate,AlunoDelete=crud(Aluno,AlunoForm,'Aluno',['nome','email','telefone'])
InstrutorList,InstrutorCreate,InstrutorUpdate,InstrutorDelete=crud(Instrutor,InstrutorForm,'Instrutor',['nome','especialidade','email'])
CursoList,CursoCreate,CursoUpdate,CursoDelete=crud(Curso,CursoForm,'Curso',['nome','instrutor','horario'])
EventoList,EventoCreate,EventoUpdate,EventoDelete=crud(Evento,EventoForm,'Evento',['titulo','data','local'])

class MatriculaList(SearchList):
    model=Matricula; template_name='core/matricula_list.html'
class MatriculaCreate(LoginRequiredMixin,MsgMixin,CreateView): model=Matricula; form_class=MatriculaForm; template_name='core/form.html'; success_url=reverse_lazy('matricula_lista'); extra_context={'titulo':'Nova matrícula'}
class MatriculaUpdate(LoginRequiredMixin,MsgMixin,UpdateView): model=Matricula; form_class=MatriculaForm; template_name='core/form.html'; success_url=reverse_lazy('matricula_lista'); extra_context={'titulo':'Editar matrícula'}
class MatriculaDelete(LoginRequiredMixin,DeleteView): model=Matricula; template_name='core/confirm_delete.html'; success_url=reverse_lazy('matricula_lista'); extra_context={'titulo':'Excluir matrícula'}
class AulaList(SearchList): model=Aula; template_name='core/aula_list.html'
class AulaCreate(LoginRequiredMixin,MsgMixin,CreateView): model=Aula; form_class=AulaForm; template_name='core/form.html'; success_url=reverse_lazy('aula_lista'); extra_context={'titulo':'Nova aula'}
class AulaUpdate(LoginRequiredMixin,MsgMixin,UpdateView): model=Aula; form_class=AulaForm; template_name='core/form.html'; success_url=reverse_lazy('aula_lista'); extra_context={'titulo':'Editar aula'}
class AulaDelete(LoginRequiredMixin,DeleteView): model=Aula; template_name='core/confirm_delete.html'; success_url=reverse_lazy('aula_lista'); extra_context={'titulo':'Excluir aula'}

@login_required
def chamada(request,pk):
    aula=get_object_or_404(Aula,pk=pk)
    matriculas=Matricula.objects.filter(curso=aula.curso,status='ATIVA').select_related('aluno')
    if request.method=='POST':
        for m in matriculas:
            presente=request.POST.get(f'm_{m.id}')=='on'
            Frequencia.objects.update_or_create(aula=aula,matricula=m,defaults={'presente':presente})
        messages.success(request,'Frequência salva.')
        return redirect('aula_lista')
    existentes={f.matricula_id:f.presente for f in Frequencia.objects.filter(aula=aula)}
    dados=[(m,existentes.get(m.id,True)) for m in matriculas]
    return render(request,'core/chamada.html',{'aula':aula,'dados':dados})

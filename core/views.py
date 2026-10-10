from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from .models import *
from .forms import *


# =========================================================
# PÁGINAS PÚBLICAS
# =========================================================

def home(request):
    return render(
        request,
        "core/home.html",
        {
            "cursos": Curso.objects.filter(ativo=True)[:6],
            "eventos": Evento.objects.filter(publicado=True)[:3],
            "midias": Midia.objects.filter(publicada=True)[:6],
        },
    )


def sobre(request):
    return render(request, "core/sobre.html")


def cursos(request):
    return render(
        request,
        "core/cursos.html",
        {"cursos": Curso.objects.filter(ativo=True)},
    )


def curso_detalhe(request, pk):
    curso = get_object_or_404(Curso, pk=pk, ativo=True)

    matriculas_ativas = Matricula.objects.filter(
        curso=curso,
        status="ATIVA"
    ).count()

    vagas_disponiveis = max(curso.vagas - matriculas_ativas, 0)

    return render(
        request,
        "core/curso_detalhe.html",
        {
            "curso": curso,
            "vagas_disponiveis": vagas_disponiveis,
        },
    )


# =========================================================
# INSCRIÇÃO PÚBLICA EM OFICINA
# =========================================================

def inscricao_oficina(request, pk):
    curso = get_object_or_404(Curso, pk=pk, ativo=True)

    matriculas_ativas = Matricula.objects.filter(
        curso=curso,
        status="ATIVA"
    ).count()

    vagas_disponiveis = max(curso.vagas - matriculas_ativas, 0)

    if vagas_disponiveis <= 0:
        messages.error(
            request,
            "No momento, não há vagas disponíveis para esta oficina."
        )
        return redirect("curso_detalhe", pk=curso.pk)

    if request.method == "POST":
        form = InscricaoOficinaForm(request.POST)

        if form.is_valid():
            nome = form.cleaned_data["nome"].strip()
            idade = form.cleaned_data["idade"]
            telefone = form.cleaned_data["telefone"].strip()
            email = form.cleaned_data["email"].strip().lower()

            # Procura primeiro pelo e-mail para evitar
            # criar o mesmo aluno várias vezes.
            aluno = Aluno.objects.filter(
                email__iexact=email
            ).first()

            if aluno is None:
                aluno = Aluno.objects.create(
                    nome=nome,
                    idade=idade,
                    telefone=telefone,
                    email=email,
                )
            else:
                # Atualiza os dados caso tenham mudado.
                aluno.nome = nome
                aluno.idade = idade
                aluno.telefone = telefone
                aluno.email = email
                aluno.save()

            # Verifica se esse aluno já está inscrito
            # nesta mesma oficina.
            matricula_existente = Matricula.objects.filter(
                aluno=aluno,
                curso=curso,
            ).first()

            if matricula_existente:
                if matricula_existente.status == "ATIVA":
                    messages.warning(
                        request,
                        "Você já está inscrito(a) nesta oficina."
                    )
                else:
                    matricula_existente.status = "ATIVA"
                    matricula_existente.save()

                    messages.success(
                        request,
                        f"Sua inscrição em {curso.nome} foi reativada com sucesso!"
                    )

                return redirect("curso_detalhe", pk=curso.pk)

            # Confere as vagas novamente antes de salvar.
            matriculas_ativas = Matricula.objects.filter(
                curso=curso,
                status="ATIVA"
            ).count()

            if matriculas_ativas >= curso.vagas:
                messages.error(
                    request,
                    "As vagas desta oficina acabaram."
                )
                return redirect("curso_detalhe", pk=curso.pk)

            Matricula.objects.create(
                aluno=aluno,
                curso=curso,
                status="ATIVA",
            )

            messages.success(
                request,
                f"Inscrição realizada com sucesso na oficina {curso.nome}!"
            )

            return redirect("curso_detalhe", pk=curso.pk)

    else:
        form = InscricaoOficinaForm()

    return render(
        request,
        "core/inscricao_oficina.html",
        {
            "curso": curso,
            "form": form,
            "vagas_disponiveis": vagas_disponiveis,
        },
    )


def eventos(request):
    return render(
        request,
        "core/eventos.html",
        {"eventos": Evento.objects.filter(publicado=True)},
    )


def galeria(request):
    return render(
        request,
        "core/galeria.html",
        {"midias": Midia.objects.filter(publicada=True)},
    )


def equipe(request):
    return render(
        request,
        "core/equipe.html",
        {"instrutores": Instrutor.objects.filter(ativo=True)},
    )


# =========================================================
# PAINEL
# =========================================================

@login_required
def painel(request):
    return render(
        request,
        "core/painel.html",
        {
            "alunos": Aluno.objects.count(),
            "instrutores": Instrutor.objects.count(),
            "cursos": Curso.objects.count(),
            "matriculas": Matricula.objects.filter(
                status="ATIVA"
            ).count(),
            "aulas": Aula.objects.count(),
            "eventos": Evento.objects.count(),
        },
    )


# =========================================================
# LISTAGENS E CRUD
# =========================================================

class SearchList(LoginRequiredMixin, ListView):
    paginate_by = 10
    search_fields = []

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()

        if q and self.search_fields:
            query = Q()

            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": q})

            qs = qs.filter(query)

        return qs

class MsgMixin:
    success_url = reverse_lazy("painel")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Registro salvo com sucesso."
        )
        return super().form_valid(form)

    def form_valid_delete(self):
        messages.success(
            self.request,
            "Registro excluído com sucesso."
        )
        return super().delete(
            self.request,
            *self.args,
            **self.kwargs
        )


def crud(model, form, prefix, fields):
    return (
        type(
            prefix + "List",
            (SearchList,),
            {
                "model": model,
                "template_name": "core/crud_list.html",
                "extra_context": {
                    "titulo": prefix,
                    "novo_url": f"{prefix.lower()}_novo",
                    "editar_url": f"{prefix.lower()}_editar",
                    "excluir_url": f"{prefix.lower()}_excluir",
                    "colunas": fields,
                },
                "search_fields": (
                    ["nome"]
                    if hasattr(model, "nome")
                    else ["titulo"]
                    if hasattr(model, "titulo")
                    else []
                ),
            },
        ),

        type(
            prefix + "Create",
            (LoginRequiredMixin, MsgMixin, CreateView),
            {
                "model": model,
                "form_class": form,
                "template_name": "core/form.html",
                "success_url": reverse_lazy(
                    f"{prefix.lower()}_lista"
                ),
                "extra_context": {
                    "titulo": f"Novo {prefix}"
                },
            },
        ),

        type(
            prefix + "Update",
            (LoginRequiredMixin, MsgMixin, UpdateView),
            {
                "model": model,
                "form_class": form,
                "template_name": "core/form.html",
                "success_url": reverse_lazy(
                    f"{prefix.lower()}_lista"
                ),
                "extra_context": {
                    "titulo": f"Editar {prefix}"
                },
            },
        ),

        type(
            prefix + "Delete",
            (SafeDeleteView,),
            {
                "model": model,
                "template_name": "core/confirm_delete.html",
                "success_url": reverse_lazy(
                    f"{prefix.lower()}_lista"
                ),
                "lista_url_name": f"{prefix.lower()}_lista",
                "extra_context": {
                    "titulo": f"Excluir {prefix}",
                    "lista_url": f"{prefix.lower()}_lista",
                },
            },
        ),
    )

class SafeDeleteView(LoginRequiredMixin, DeleteView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        response["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            return redirect(self.get_list_url())

        return super().get(request, *args, **kwargs)

    def get_list_url(self):
        return reverse(self.lista_url_name)

    def form_valid(self, form):
        messages.success(
            self.request,
            "Registro excluído com sucesso."
        )
        return super().form_valid(form)

AlunoList, AlunoCreate, AlunoUpdate, AlunoDelete = crud(
    Aluno,
    AlunoForm,
    "Aluno",
    ["nome", "email", "telefone"],
)

InstrutorList, InstrutorCreate, InstrutorUpdate, InstrutorDelete = crud(
    Instrutor,
    InstrutorForm,
    "Instrutor",
    ["nome", "especialidade", "email"],
)

CursoList, CursoCreate, CursoUpdate, CursoDelete = crud(
    Curso,
    CursoForm,
    "Curso",
    ["nome", "instrutor", "horario"],
)

EventoList, EventoCreate, EventoUpdate, EventoDelete = crud(
    Evento,
    EventoForm,
    "Evento",
    ["titulo", "data", "local"],
)

MidiaList, MidiaCreate, MidiaUpdate, MidiaDelete = crud(
    Midia,
    MidiaForm,
    "Midia",
    ["titulo", "data"],
)


# =========================================================
# MATRÍCULAS
# =========================================================

class MatriculaList(SearchList):
    model = Matricula
    template_name = "core/matricula_list.html"


class MatriculaCreate(LoginRequiredMixin, MsgMixin, CreateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = "core/form.html"
    success_url = reverse_lazy("matricula_lista")
    extra_context = {"titulo": "Nova matrícula"}


class MatriculaUpdate(LoginRequiredMixin, MsgMixin, UpdateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = "core/form.html"
    success_url = reverse_lazy("matricula_lista")
    extra_context = {"titulo": "Editar matrícula"}


class MatriculaDelete(LoginRequiredMixin, DeleteView):
    model = Matricula
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("matricula_lista")
    extra_context = {"titulo": "Excluir matrícula"}


# =========================================================
# AULAS
# =========================================================

class AulaList(SearchList):
    model = Aula
    template_name = "core/aula_list.html"


class AulaCreate(LoginRequiredMixin, MsgMixin, CreateView):
    model = Aula
    form_class = AulaForm
    template_name = "core/form.html"
    success_url = reverse_lazy("aula_lista")
    extra_context = {"titulo": "Nova aula"}


class AulaUpdate(LoginRequiredMixin, MsgMixin, UpdateView):
    model = Aula
    form_class = AulaForm
    template_name = "core/form.html"
    success_url = reverse_lazy("aula_lista")
    extra_context = {"titulo": "Editar aula"}


class AulaDelete(LoginRequiredMixin, DeleteView):
    model = Aula
    template_name = "core/confirm_delete.html"
    success_url = reverse_lazy("aula_lista")
    extra_context = {"titulo": "Excluir aula"}


# =========================================================
# CHAMADA / FREQUÊNCIA
# =========================================================

@login_required
def chamada(request, pk):
    aula = get_object_or_404(Aula, pk=pk)

    matriculas = Matricula.objects.filter(
        curso=aula.curso,
        status="ATIVA",
    ).select_related("aluno")

    if request.method == "POST":

        for matricula in matriculas:
            presente = (
                request.POST.get(
                    f"m_{matricula.id}"
                ) == "on"
            )

            Frequencia.objects.update_or_create(
                aula=aula,
                matricula=matricula,
                defaults={
                    "presente": presente
                },
            )

        messages.success(
            request,
            "Frequência salva."
        )

        return redirect("aula_lista")

    existentes = {
        frequencia.matricula_id: frequencia.presente
        for frequencia in Frequencia.objects.filter(
            aula=aula
        )
    }

    dados = [
        (
            matricula,
            existentes.get(matricula.id, True),
        )
        for matricula in matriculas
    ]

    return render(
        request,
        "core/chamada.html",
        {
            "aula": aula,
            "dados": dados,
        },
    )